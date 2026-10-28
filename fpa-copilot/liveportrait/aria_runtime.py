"""Local ARIA CLI. Standard-library-only until prepare/doctor loads dependencies."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import uuid

UPSTREAM_SHA = '9b294b3d0536135442ea73cb01e6cb3ca7029dd3'
WEIGHTS_SHA = '82a4fa6735ca58432b6ce39301b4b9ee066dea47'
PORTRAIT_SHA = '9889d86d17f07437243204107a91ed7ab4a49a5a9d1841ec56c59d117247d958'
HERE = Path(__file__).resolve().parent
WEIGHTS = (
    'liveportrait/base_models/appearance_feature_extractor.pth',
    'liveportrait/base_models/motion_extractor.pth',
    'liveportrait/base_models/spade_generator.pth',
    'liveportrait/base_models/warping_module.pth',
    'liveportrait/retargeting_models/stitching_retargeting_module.pth',
    'liveportrait/landmark.onnx',
    'insightface/models/buffalo_l/2d106det.onnx',
    'insightface/models/buffalo_l/det_10g.onnx',
)


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else _hash_stream(stream)


def _hash_stream(stream):
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(block)
    return digest.hexdigest()


def approved(path):
    if not path.is_file() or sha256(path) != PORTRAIT_SHA:
        raise RuntimeError(f'Approved portrait missing or changed: {path}. Restore it from the reviewed package; no substitute will be used.')


def preserve_portrait(root):
    source, target = HERE / 'aria-approved.png', root / 'aria-approved.png'
    approved(source)
    if target.exists():
        approved(target)  # Never overwrite an unknown image.
    else:
        with source.open('rb') as src, target.open('xb') as dst:
            shutil.copyfileobj(src, dst)
    approved(target)


def checkout(root):
    repo = root / f'LivePortrait-{UPSTREAM_SHA}'
    head = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    if head != UPSTREAM_SHA:
        raise RuntimeError('Upstream revision differs. Rerun install_mac.sh.')
    dirty = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain', '--untracked-files=no'], text=True)
    if dirty.strip():
        raise RuntimeError('Tracked upstream files have changed. Preserve your changes and restore the pinned checkout.')
    return repo


def check_weights(repo):
    for name in WEIGHTS:
        path = repo / 'pretrained_weights' / name
        if not path.is_file() or path.stat().st_size < 1024:
            raise RuntimeError(f'Missing/incomplete model: {path}. Rerun install_mac.sh.')
        with path.open('rb') as stream:
            if stream.read(80).startswith(b'version https://git-lfs'):
                raise RuntimeError(f'Git LFS pointer instead of model: {path}')


def prepare(root):
    from huggingface_hub import hf_hub_download
    repo = checkout(root)
    preserve_portrait(root)
    for name in WEIGHTS:
        hf_hub_download(repo_id='KlingTeam/LivePortrait', revision=WEIGHTS_SHA,
                        filename=name, local_dir=str(repo / 'pretrained_weights'))
    check_weights(repo)
    print('Approved portrait and eight human model files prepared.')


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)
    ], text=True))


def video_stream(info):
    videos = [s for s in info.get('streams', []) if s.get('codec_type') == 'video']
    if not videos or float(info.get('format', {}).get('duration', 0)) <= 0:
        raise RuntimeError('Input/output must contain a video stream with positive duration.')
    return videos[0]


def doctor(root):
    report = root / 'environment-check.json'
    report.unlink(missing_ok=True)  # A failed recheck must not leave stale success.
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise RuntimeError('Verification requires native arm64 macOS.')
    if sys.version_info[:2] != (3, 10):
        raise RuntimeError('Use the managed Python 3.10 environment.')
    repo = checkout(root)
    approved(root / 'aria-approved.png')
    check_weights(repo)
    for executable in ('ffmpeg', 'ffprobe'):
        subprocess.run([executable, '-version'], check=True, stdout=subprocess.DEVNULL)
    import torch
    import onnxruntime as ort
    if not torch.backends.mps.is_available():
        raise RuntimeError('PyTorch MPS unavailable. Check native arm64 Python and macOS; do not proceed with CUDA.')
    if 'CPUExecutionProvider' not in ort.get_available_providers():
        raise RuntimeError('ONNX CPU provider missing.')
    os.chdir(repo)
    sys.path.insert(0, str(repo))
    from src.config.inference_config import InferenceConfig
    from src.config.crop_config import CropConfig
    from src.live_portrait_pipeline import LivePortraitPipeline
    from PIL import Image
    import numpy as np
    pipeline = LivePortraitPipeline(InferenceConfig(flag_use_half_precision=False), CropConfig())
    crop = pipeline.cropper.crop_source_image(np.asarray(Image.open(root / 'aria-approved.png').convert('RGB')), CropConfig())
    if crop is None:
        raise RuntimeError('No face detected in approved ARIA portrait. Keep original and inspect crop settings.')
    # Exercise the neural renderer, including 5-D grid sampling/MPS fallback.
    wrapper = pipeline.live_portrait_wrapper
    source = wrapper.prepare_source(crop['img_crop_256x256'])
    feature = wrapper.extract_feature_3d(source)
    kp = wrapper.transform_keypoint(wrapper.get_kp_info(source))
    rendered = wrapper.warp_decode(feature, kp, kp)['out']
    if not bool(torch.isfinite(rendered).all().item()):
        raise RuntimeError('Renderer produced non-finite values.')
    report.write_text(json.dumps({
        'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'environment-checked',
        'upstream': UPSTREAM_SHA, 'weights_revision': WEIGHTS_SHA, 'portrait_sha256': PORTRAIT_SHA,
        'python': sys.version, 'torch': torch.__version__, 'onnxruntime': ort.__version__,
        'mps': True, 'face_detected': True, 'single_frame_renderer': True,
        'animation_visual_review': 'pending',
    }, indent=2) + '\n')
    with (root / 'installed-packages.txt').open('w') as packages:
        subprocess.run([sys.executable, '-m', 'pip', 'freeze'], check=True, stdout=packages)
    print(f'Environment, face detection and one neural frame passed. Report: {report}')
    print('Speech animation, teeth, blinking and temporal quality still require a driving-video render and review.')


def inference_command(repo, source, driving, output):
    return [sys.executable, str(repo / 'inference.py'), '-s', str(source), '-d', str(driving),
            '-o', str(output), '--flag_crop_driving_video', '--animation_region', 'all',
            '--driving_multiplier', '1.0', '--audio_priority', 'driving',
            '--no_flag_use_half_precision']


def animate(root, driving):
    repo = checkout(root)
    source = root / 'aria-approved.png'
    approved(source)
    check_weights(repo)
    if not (root / 'environment-check.json').is_file():
        raise RuntimeError('Run verify_mac.sh successfully before animation.')
    if not driving.is_file() or driving.suffix.lower() not in ('.mp4', '.mov', '.m4v'):
        raise RuntimeError('Supply an existing .mp4/.mov/.m4v driving video, not audio or a pickle template.')
    info = probe(driving)
    video_stream(info)
    if not any(s.get('codec_type') == 'audio' for s in info['streams']):
        raise RuntimeError('Speaking workflow needs a driving video with the intended speech audio.')
    # Each run gets a new directory so an old MP4 cannot masquerade as a successful render.
    output = root / 'animations' / (datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
    output.mkdir(parents=True)
    env = dict(os.environ, PYTORCH_ENABLE_MPS_FALLBACK='1')
    subprocess.run(inference_command(repo, source, driving, output), cwd=repo, env=env, check=True)
    result = output / f'aria-approved--{driving.stem}.mp4'
    result_info = probe(result)
    video_stream(result_info)
    if not any(s.get('codec_type') == 'audio' for s in result_info['streams']):
        raise RuntimeError('Generated MP4 is missing speech audio.')
    # Fully decode the output, catching corruption rather than only inspecting its header.
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(result), '-f', 'null', '-'], check=True)
    approved(source)
    (output / 'render-check.json').write_text(json.dumps({
        'status': 'render-decodes-with-audio', 'portrait_sha256': PORTRAIT_SHA,
        'upstream': UPSTREAM_SHA, 'weights_revision': WEIGHTS_SHA,
        'result': str(result), 'media': result_info,
        'visual_review': 'pending: identity, suit, teeth, lip timing, blinks, head motion, seams',
    }, indent=2) + '\n')
    print(f'Render and audio decode passed: {result}')
    print('Open this MP4 in QuickTime. Review identity, teeth, lip timing, blinking and head motion before publication.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'doctor', 'animate'))
    parser.add_argument('--root', type=Path, default=Path.home() / 'ARIA-LivePortrait')
    parser.add_argument('--driving', type=Path)
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if args.action == 'animate':
        animate(root, (args.driving or root / 'driving.mp4').expanduser().resolve())
    else:
        globals()[args.action](root)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        sys.exit(1)
