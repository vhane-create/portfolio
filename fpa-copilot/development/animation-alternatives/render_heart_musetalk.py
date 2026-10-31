"""Audio-driven mouth rendering against actual ARIA source frames, without looping.

Requires the inspected MuseTalk Apple Silicon port and official MuseTalk 1.5
weights. This is an offline renderer, not a claim of real-time conversation.
"""
import argparse
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--engine', type=Path, required=True)
    p.add_argument('--video', type=Path, required=True)
    p.add_argument('--audio', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--seconds', type=float)
    p.add_argument('--batch', type=int, default=2)
    p.add_argument('--threads', type=int, default=4)
    p.add_argument('--bf16', action='store_true')
    p.add_argument('--channels-last', action='store_true')
    p.add_argument('--speech-ranges', type=Path, help='Only repaint during these timed speech passages; retain original video elsewhere')
    p.add_argument('--small-face-fallback', action='store_true', help='Find and enlarge distant faces before landmark detection')
    p.add_argument('--bbox-overrides', type=Path, help='Render only these source frame indices with reviewed interpolated face boxes')
    a = p.parse_args()
    a.engine, a.video, a.audio, a.output = [x.resolve() for x in (a.engine, a.video, a.audio, a.output)]
    speech_ranges = json.loads(a.speech_ranges.resolve().read_text()) if a.speech_ranges else None
    overrides = json.loads(a.bbox_overrides.resolve().read_text()) if a.bbox_overrides else None
    sys.path.insert(0, str(a.engine))
    os.chdir(a.engine)
    import cv2
    import numpy as np
    import torch
    from accelerate import init_empty_weights
    from diffusers import UNet2DConditionModel
    from transformers import WhisperModel
    from musetalk.models.vae import VAE
    from musetalk.models.unet import PositionalEncoding
    from musetalk.utils.audio_processor import AudioProcessor
    from musetalk.utils.preprocessing import _landmarks_px, coord_placeholder
    from musetalk.utils.face_parsing import FaceParsing
    from musetalk.utils.blending import get_image
    torch.set_num_threads(a.threads)
    torch.manual_seed(7)
    cv2.setNumThreads(1)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def landmarks(frame):
        pts = _landmarks_px(frame)
        if pts is not None or not a.small_face_fallback:
            return pts
        faces = cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 1.1, 3, minSize=(25,25))
        if len(faces) == 0:
            return None
        x,y,w,h = max(faces, key=lambda b: b[2]*b[3])
        x0,y0=max(0,x-w//2),max(0,y-h//2)
        x1,y1=min(frame.shape[1],x+w+w//2),min(frame.shape[0],y+h+h//2)
        cropped = _landmarks_px(frame[y0:y1,x0:x1])
        return cropped + np.array([x0,y0]) if cropped is not None else None
    device = torch.device('cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu'))
    dtype = torch.bfloat16 if a.bf16 else torch.float32
    if a.bf16 and device.type != 'cpu':
        raise ValueError('--bf16 is only tested for this CPU preview')
    cap = cv2.VideoCapture(str(a.video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if not cap.isOpened() or fps <= 0:
        raise ValueError('Source video cannot be read')
    duration = count / fps
    audio_meta = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(a.audio)]))
    audio_duration = float(audio_meta['format']['duration'])
    if audio_duration > duration + 1 / fps:
        raise ValueError('Audio exceeds source duration; repeating or freezing source is disabled')
    first = round(a.start * fps)
    last = min(count, round((a.start + a.seconds) * fps)) if a.seconds else count
    if first < 0 or last <= first:
        raise ValueError('Invalid frame interval')
    total = last - first
    print(json.dumps({'device':str(device),'dtype':str(dtype),'frames':total,'fps':fps,'source_seconds':duration}), flush=True)
    started = time.perf_counter()
    with torch.inference_mode():
        vae = VAE(model_path='models/sd-vae')
        vae.vae.to(device=device, dtype=dtype).eval()
        if a.channels_last:
            vae.vae.to(memory_format=torch.channels_last)
        config = json.loads(Path('models/musetalkV15/musetalk.json').read_text())
        with init_empty_weights():
            unet = UNet2DConditionModel(**config)
        weights = torch.load('models/musetalkV15/unet.pth', map_location='cpu', mmap=True, weights_only=True)
        unet.load_state_dict(weights, assign=True)
        unet.to(device=device, dtype=dtype).eval()
        if a.channels_last:
            unet.to(memory_format=torch.channels_last)
        del weights
        gc.collect()
        pe = PositionalEncoding(d_model=384).to(device=device, dtype=dtype)
        ap = AudioProcessor(feature_extractor_path='models/whisper')
        whisper = WhisperModel.from_pretrained('models/whisper').to(device=device).eval()
        features, audio_length = ap.get_audio_feature(str(a.audio))
        prompts = ap.get_whisper_chunk(features, device, torch.float32, whisper, audio_length, fps=fps)
        del whisper, features, ap
        gc.collect()
        parser = FaceParsing()
        a.output.parent.mkdir(parents=True, exist_ok=True)
        silent = a.output.with_suffix('.silent.mp4')
        encoder = subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(silent)], stdin=subprocess.PIPE)
        cap.set(cv2.CAP_PROP_POS_FRAMES, first)
        processed, missing = 0, []
        timings = []
        try:
            while processed < total:
                originals, boxes, latents, batch_prompts = [], [], [], []
                tick = time.perf_counter()
                for j in range(min(a.batch, total - processed)):
                    ok, frame = cap.read()
                    if not ok:
                        raise RuntimeError('Source ended early; no repeated frame will be inserted')
                    originals.append(frame)
                    current_time = (first + processed + j) / fps
                    active = speech_ranges is None or any(x['start'] - .1 <= current_time <= x['end'] + .1 for x in speech_ranges)
                    override_key = str(first + processed + j)
                    if overrides is not None:
                        active = active and override_key in overrides
                    box = tuple(overrides[override_key]) if active and overrides is not None else None
                    pts = landmarks(frame) if active and box is None else None
                    if pts is not None:
                        mid_y = int(pts[6, 1])
                        y2 = min(height, int(pts[:, 1].max()) + 10)
                        y1 = max(0, mid_y - (int(pts[:, 1].max()) - mid_y))
                        x1, x2 = max(0, int(pts[:, 0].min())), min(width, int(pts[:, 0].max()))
                        if x2 > x1 and y2 > y1:
                            box = (x1, y1, x2, y2)
                    if box is not None:
                        x1,y1,x2,y2=box
                        crop = cv2.resize(frame[y1:y2, x1:x2], (256,256), interpolation=cv2.INTER_LANCZOS4)
                        latents.append(vae.get_latents_for_unet(crop))
                        idx = first + processed + j
                        batch_prompts.append(prompts[min(idx, len(prompts)-1)])
                    if box is None and active:
                        missing.append(first + processed + j)
                    boxes.append(box)
                generated = iter([])
                if latents:
                    inp = torch.cat(latents).to(device=device, dtype=dtype)
                    conditioning = pe(torch.stack(batch_prompts).to(device=device,dtype=dtype))
                    predicted = unet(inp, torch.tensor([0],device=device), encoder_hidden_states=conditioning).sample
                    generated = iter(vae.decode_latents(predicted))
                for frame, box in zip(originals, boxes):
                    if box is not None:
                        x1,y1,x2,y2 = box
                        face = cv2.resize(next(generated), (x2-x1,y2-y1), interpolation=cv2.INTER_LANCZOS4)
                        frame = get_image(frame, face, box, fp=parser)
                    encoder.stdin.write(frame.tobytes())
                processed += len(originals)
                elapsed = time.perf_counter() - tick
                timings.append(elapsed)
                print(json.dumps({'rendered':processed,'total':total,'batch_seconds':round(elapsed,3),'elapsed_seconds':round(time.perf_counter()-started,2)}), flush=True)
            encoder.stdin.close()
            if encoder.wait() != 0:
                raise RuntimeError('Video encoding failed')
        except BaseException:
            encoder.kill()
            raise
        finally:
            cap.release()
        seconds = total / fps
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-ss',str(first/fps),'-i',str(a.audio),'-map','0:v:0','-map','1:a:0','-t',str(seconds),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(a.output)],check=True)
        silent.unlink()
        report = {'renderer':'MuseTalk 1.5','source':a.video.name,'audio':a.audio.name,'output':a.output.name,'frames':total,'fps':fps,'seconds':seconds,'first_frame':first,'missing_face_frames':missing,'render_seconds':time.perf_counter()-started,'batch_seconds':timings,'dtype':str(dtype),'device':str(device),'status':'rendered; visual and audible review required; not a live conversation'}
        a.output.with_suffix('.json').write_text(json.dumps(report,indent=2))
        print(json.dumps(report),flush=True)


if __name__ == '__main__':
    main()
