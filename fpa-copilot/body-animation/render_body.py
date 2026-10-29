"""Offline ARIA body-animation experiment; not a live animation service.

Consumes an already-generated Heart WAV. Never synthesizes or substitutes a voice.
Model output requires human identity, anatomy and lip-sync review before publication.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import uuid

UPSTREAM = '7e89489ca51c0d008fc1963ec6c03fc5bd0b9397'
PORTRAIT_SHA256 = 'e58e11065f0297628762ae3c37126742619f1633e0aaf66001a89fe19de62f75'
PROMPT = ('The same full-body female android in the reference image speaks directly '
          'to the viewer, with small relaxed conversational hand gestures and natural '
          'blinks. Preserve her face, long wavy black hair, black executive suit, '
          'robotic details and body proportions. Keep the camera stationary and her '
          'entire body in frame. No scene cuts.')


def digest(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)
    ], text=True))


def validate_inputs(image, audio):
    if digest(image) != PORTRAIT_SHA256:
        raise ValueError('The image is not ARIA’s approved full-body source. No substitute will be used.')
    if audio.suffix.lower() != '.wav':
        raise ValueError('Supply an already-generated Heart WAV, not the reference woman’s audio.')
    info = probe(audio)
    duration = float(info.get('format', {}).get('duration', 0))
    if not any(s['codec_type'] == 'audio' for s in info['streams']) or not 0.5 <= duration <= 3.2:
        raise ValueError('This initial render supports 0.5–3.2 seconds of Heart audio; longer replies are not implemented.')
    # The upstream pipeline snaps temporal length to 4n+1 frames.
    frames = 4 * math.ceil((duration * 25 - 1) / 4) + 1
    return duration, frames


def command(repo, weights, image, audio, output, frames):
    return [sys.executable, str(repo / 'infer_flash.py'),
            '--image_path', str(image), '--audio_path', str(audio), '--prompt', PROMPT,
            '--config_path', str(repo / 'config/config.yaml'),
            '--model_name', str(weights / 'Wan2.1-Fun-V1.1-1.3B-InP'),
            '--transformer_path', str(weights / 'transformer/diffusion_pytorch_model.safetensors'),
            '--wav2vec_model_dir', str(weights / 'chinese-wav2vec2-base'),
            '--save_path', str(output), '--video_length', str(frames), '--fps', '25',
            '--num_inference_steps', '8', '--sample_size', '768', '768', '--seed', '43']


def environment(repo, weights):
    problems = []
    try:
        import torch
        if not torch.cuda.is_available():
            problems.append('CUDA GPU unavailable. No CPU or replacement-avatar fallback is configured.')
    except ImportError:
        problems.append('PyTorch and the CUDA rendering environment are not installed.')
    try:
        actual = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True, stderr=subprocess.DEVNULL).strip()
        if actual != UPSTREAM:
            problems.append('EchoMimicV3 checkout differs from the reviewed revision.')
        dirty = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain', '--untracked-files=no'], text=True)
        if dirty.strip():
            problems.append('The upstream checkout has modified tracked files.')
    except (OSError, subprocess.CalledProcessError):
        problems.append('The pinned EchoMimicV3 checkout is missing.')
    for name in ['Wan2.1-Fun-V1.1-1.3B-InP/model_index.json',
                 'transformer/diffusion_pytorch_model.safetensors', 'chinese-wav2vec2-base/config.json']:
        if not (weights / name).is_file():
            problems.append('Missing model component: ' + name)
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--weights', type=Path, required=True)
    parser.add_argument('--image', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/aria-full-body-approved.png')
    parser.add_argument('--heart-audio', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, default=Path('body-renders'))
    parser.add_argument('--check', action='store_true', help='Validate inputs and report blockers without rendering or downloading.')
    args = parser.parse_args()
    repo, weights, image, audio = [p.expanduser().resolve() for p in (args.repo, args.weights, args.image, args.heart_audio)]
    duration, frames = validate_inputs(image, audio)
    problems = environment(repo, weights)
    if args.check:
        print(json.dumps({'status': 'blocked' if problems else 'environment-ready-unrendered',
                          'blockers': problems, 'input_seconds': duration, 'frames': frames,
                          'upstream_revision': UPSTREAM, 'voice': 'supplied Heart WAV; no synthesis',
                          'animation_verified': False, 'live_conversation': False}, indent=2))
        return 2 if problems else 0
    if problems:
        raise ValueError('; '.join(problems))
    output = args.output_root.expanduser().resolve() / uuid.uuid4().hex
    output.mkdir(parents=True)
    conditioning = output / 'heart-conditioning.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(audio), '-af', 'apad',
                    '-t', str(frames / 25), str(conditioning)], check=True)
    subprocess.run(command(repo, weights, image, conditioning, output, frames), cwd=repo, check=True)
    rendered = output / (image.stem + '_output.mp4')
    info = probe(rendered)
    if not any(s['codec_type'] == 'video' for s in info['streams']):
        raise ValueError('Renderer did not produce a video stream.')
    # Preserve the exact original Heart waveform as a lossless audio stream. Never
    # retain any model-generated voice. Pad the final video frame for rounding only.
    final = output / 'aria-heart-body.mkv'
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(rendered), '-i', str(audio),
                    '-map', '0:v:0', '-map', '1:a:0', '-vf', 'tpad=stop_mode=clone:stop_duration=1',
                    '-t', str(duration), '-c:v', 'libx264', '-c:a', 'copy', str(final)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(final), '-f', 'null', '-'], check=True)
    (output / 'render-report.json').write_text(json.dumps({
        'source_image_sha256': digest(image), 'source_heart_sha256': digest(audio),
        'upstream_revision': UPSTREAM, 'result': str(final), 'decoded': True,
        'identity_review': 'pending', 'movement_review': 'pending', 'lip_sync_review': 'pending',
        'live_conversation': False}, indent=2) + '\n')
    print('Rendered and decoded, but not visually approved: ' + str(final))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        raise SystemExit(1)
