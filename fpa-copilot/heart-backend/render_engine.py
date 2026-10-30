"""Single-avatar neural engine; no HTTP server or alternate voice provider.

Core frame preparation and compositing adapted from the bundled MuseTalk-Mac
server. Models and approved source are retained for this process's lifetime.
"""
import os,sys,json,time,glob,shutil,tempfile,subprocess
from pathlib import Path
from types import SimpleNamespace
import zipfile

state={}
EXTRA_MARGIN=10
class HTTPException(RuntimeError):
    def __init__(self,status_code,detail): super().__init__(detail)


def initialize(upstream, source):
    global torch,cv2,np,datagen,get_video_fps,get_landmark_and_bbox,coord_placeholder,get_image_prepare_material,get_image_blending
    os.chdir(upstream)
    sys.path.insert(0,str(upstream))
    import torch,cv2,numpy as np
    from diffusers import UNet2DConditionModel
    from transformers import WhisperModel
    from musetalk.models.vae import VAE
    from musetalk.models.unet import PositionalEncoding
    from musetalk.utils.audio_processor import AudioProcessor
    from musetalk.utils.face_parsing import FaceParsing
    from musetalk.utils.preprocessing import get_landmark_and_bbox,coord_placeholder
    from musetalk.utils.blending import get_image_prepare_material,get_image_blending
    from musetalk.utils.utils import datagen,get_video_fps
    torch.set_num_threads(4)
    cv2.setNumThreads(2)
    device=torch.device('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')
    path=Path('models/musetalkV15/unet.pth')
    config=json.loads(Path('models/musetalkV15/musetalk.json').read_text())
    with torch.device('meta'): model=UNet2DConditionModel(**config)
    weights=torch.load(path,map_location='cpu',weights_only=True,mmap=zipfile.is_zipfile(path))
    model.load_state_dict(weights,strict=True,assign=True)
    del weights
    if any(t.is_meta for t in list(model.parameters())+list(model.buffers())):
        raise RuntimeError('Animation model has uninitialized tensors.')
    model=model.eval().requires_grad_(False)
    vae=VAE(model_path='./models/sd-vae')
    pe=PositionalEncoding()
    if device.type != 'cpu': model=model.half();vae.vae=vae.vae.half();pe=pe.half()
    model=model.to(device);vae.vae=vae.vae.to(device);pe=pe.to(device)
    whisper=WhisperModel.from_pretrained('./models/whisper',local_files_only=True).to(device=device,dtype=model.dtype).eval().requires_grad_(False)
    state.update(device=device,unet=SimpleNamespace(model=model),vae=vae,pe=pe,whisper=whisper,audio_processor=AudioProcessor('./models/whisper'),weight_dtype=model.dtype,timesteps=torch.tensor([0],device=device),fp=FaceParsing(left_cheek_width=90,right_cheek_width=90))
    with torch.inference_mode(): return prepare_avatar(source.read_bytes())


def render(avatar, wav):
    with torch.inference_mode(): return run_lipsync(avatar,wav.read_bytes(),batch_size=1)

def _detect_media_kind(data: bytes) -> str:
    """Return 'image' or 'video' by inspecting magic bytes."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image"
    if data[:3] == b"\xff\xd8\xff" or data[6:10] in (b"JFIF", b"Exif"):
        return "image"
    return "video"

def _write_input_media(tmp: str, data: bytes) -> tuple[list[str], float]:
    """Write incoming media to tmp, return (image_list, fps)."""
    kind = _detect_media_kind(data)
    if kind == "image":
        img_path = os.path.join(tmp, "in.png")
        with open(img_path, "wb") as f:
            f.write(data)
        return [img_path], 25.0

    vid = os.path.join(tmp, "in.mp4")
    with open(vid, "wb") as f:
        f.write(data)
    frames_dir = os.path.join(tmp, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", vid, "-start_number", "0",
         f"{frames_dir}/%08d.png"],
        check=True,
    )
    img_list = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    fps = get_video_fps(vid)
    return img_list, fps

def prepare_avatar(video_bytes: bytes) -> dict:
    """Run the expensive one-time prep: frames, landmarks, VAE encode."""
    tmp = tempfile.mkdtemp(prefix="mt_avatar_")
    try:
        img_list, fps = _write_input_media(tmp, video_bytes)
        coord_list, frame_list = get_landmark_and_bbox(img_list, 0)

        vae = state["vae"]
        fp = state["fp"]
        input_latent_list = []
        valid_coords = []
        valid_frames = []
        mask_list = []
        crop_box_list = []
        for bbox, frame in zip(coord_list, frame_list):
            if bbox == coord_placeholder:
                continue
            x1, y1, x2, y2 = bbox
            y2 = min(y2 + EXTRA_MARGIN, frame.shape[0])
            crop = frame[y1:y2, x1:x2]
            crop = cv2.resize(crop, (256, 256), interpolation=cv2.INTER_LANCZOS4)
            latents = vae.get_latents_for_unet(crop)
            input_latent_list.append(latents)
            valid_coords.append((x1, y1, x2, y2))
            valid_frames.append(frame)
            # Precompute face-parse mask + crop box for this source frame.
            # The mask depends only on the source frame, not on the generated
            # mouth — so we do this once during warmup, saving ~7s per lipsync.
            mask_array, crop_box = get_image_prepare_material(
                frame, [x1, y1, x2, y2], fp=fp, mode="jaw"
            )
            mask_list.append(mask_array)
            crop_box_list.append(crop_box)

        if not input_latent_list:
            raise HTTPException(status_code=400, detail="No face detected in input")

        return {
            "fps": fps,
            "coord_list_cycle": valid_coords + valid_coords[::-1],
            "frame_list_cycle": valid_frames + valid_frames[::-1],
            "input_latent_list_cycle": input_latent_list + input_latent_list[::-1],
            "mask_list_cycle": mask_list + mask_list[::-1],
            "crop_box_list_cycle": crop_box_list + crop_box_list[::-1],
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def run_lipsync(avatar: dict, audio_bytes: bytes, batch_size: int = 16) -> bytes:
    """Given a prepared avatar and audio bytes, return final mp4 bytes."""
    prof = {}
    _t0 = time.time()

    tmp = tempfile.mkdtemp(prefix="mt_lip_")
    try:
        wav = os.path.join(tmp, "in.wav")
        with open(wav, "wb") as f:
            f.write(audio_bytes)

        device = state["device"]
        pe = state["pe"]
        unet = state["unet"]
        vae = state["vae"]
        whisper = state["whisper"]
        audio_processor = state["audio_processor"]
        weight_dtype = state["weight_dtype"]
        timesteps = state["timesteps"]
        fp = state["fp"]

        fps = avatar["fps"]
        _t = time.time()
        whisper_features, librosa_len = audio_processor.get_audio_feature(wav)
        whisper_chunks = audio_processor.get_whisper_chunk(
            whisper_features, device, weight_dtype, whisper, librosa_len,
            fps=fps, audio_padding_length_left=2, audio_padding_length_right=2,
        )
        prof["audio_ms"] = int((time.time() - _t) * 1000)

        coord_cycle = avatar["coord_list_cycle"]
        frame_cycle = avatar["frame_list_cycle"]
        latent_cycle = avatar["input_latent_list_cycle"]
        mask_cycle = avatar["mask_list_cycle"]
        crop_box_cycle = avatar["crop_box_list_cycle"]

        gen = datagen(whisper_chunks, latent_cycle, batch_size, 0, device)
        res_frame_list = []
        _t = time.time()
        with torch.no_grad():
            for whisper_batch, latent_batch in gen:
                audio_feat = pe(whisper_batch)
                latent_batch = latent_batch.to(dtype=unet.model.dtype)
                pred = unet.model(
                    latent_batch, timesteps, encoder_hidden_states=audio_feat
                ).sample
                recon = vae.decode_latents(pred)
                for r in recon:
                    res_frame_list.append(r)
        prof["unet_vae_ms"] = int((time.time() - _t) * 1000)
        prof["frames"] = len(res_frame_list)

        # Build output video by piping BGR frames directly into ffmpeg's stdin.
        # Face-parse masks are precomputed per source frame during warmup, so
        # we can use get_image_blending which is a pure compositing op.
        silent = os.path.join(tmp, "silent.mp4")
        # Frame size from first available frame
        h, w = frame_cycle[0].shape[:2]
        _t = time.time()
        ff_proc = subprocess.Popen(
            [
                "ffmpeg", "-y", "-v", "error",
                "-f", "rawvideo", "-pix_fmt", "bgr24",
                "-s", f"{w}x{h}", "-r", str(fps),
                "-i", "-",
                "-vcodec", "libx264", "-pix_fmt", "yuv420p",
                "-preset", "veryfast", "-crf", "18",
                silent,
            ],
            stdin=subprocess.PIPE,
        )
        assert ff_proc.stdin is not None
        blend_ms = 0
        pipe_ms = 0
        for i, res_frame in enumerate(res_frame_list):
            idx = i % len(coord_cycle)
            x1, y1, x2, y2 = coord_cycle[idx]
            ori = frame_cycle[idx]  # no deepcopy: get_image_blending doesn't mutate
            try:
                rs = cv2.resize(res_frame.astype(np.uint8), (x2 - x1, y2 - y1))
            except Exception:
                continue
            _t2 = time.time()
            combined = get_image_blending(
                ori, rs, [x1, y1, x2, y2],
                mask_cycle[idx], crop_box_cycle[idx],
            )
            blend_ms += int((time.time() - _t2) * 1000)
            _t3 = time.time()
            ff_proc.stdin.write(np.ascontiguousarray(combined).tobytes())
            pipe_ms += int((time.time() - _t3) * 1000)
        ff_proc.stdin.close()
        if ff_proc.wait() != 0:
            raise RuntimeError("Animation video encoder failed.")
        prof["blend_ms"] = blend_ms
        prof["pipe_ms"] = pipe_ms
        prof["ffmpeg_encode_ms"] = int((time.time() - _t) * 1000) - blend_ms - pipe_ms

        final = os.path.join(tmp, "final.mp4")
        _t = time.time()
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", wav, "-i", silent,
             "-c:v", "copy", "-c:a", "aac", "-shortest", final],
            check=True,
        )
        prof["ffmpeg_mux_ms"] = int((time.time() - _t) * 1000)
        with open(final, "rb") as f:
            mp4 = f.read()
        prof["total_ms"] = int((time.time() - _t0) * 1000)
        print(f"[profile] {prof}", flush=True)
        return mp4
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
