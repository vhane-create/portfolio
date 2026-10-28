"""Recreate ARIA's separate voice/MuseTalk environments on an Apple Silicon Mac.
Existing environments and runtime code are retained. Model downloads require a flag.
"""
from pathlib import Path
import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import venv


def run(args):
    print('Running:', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), check=True)


def copy_if_missing(source, target):
    if target.exists():
        if hashlib.sha256(source.read_bytes()).digest() != hashlib.sha256(target.read_bytes()).digest():
            raise RuntimeError('Existing file differs; nothing overwritten: ' + str(target))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open('rb') as src, target.open('xb') as dst:
        shutil.copyfileobj(src, dst)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.home() / 'ARIA-LivePortrait')
    parser.add_argument('--usb', type=Path, default=Path('/Volumes/NO NAME'))
    parser.add_argument('--download-models', action='store_true')
    args = parser.parse_args()
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise SystemExit('This installer requires native Apple Silicon macOS. Static playback works on other systems.')
    project = Path(__file__).resolve().parent
    root = args.root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(root).free < 8 * 1024**3:
        raise SystemExit('Keep at least 8 GB free before installation; additional space may be needed for environments and swap.')
    conda = shutil.which('conda') or str(Path.home() / 'miniforge3/bin/conda')
    if not Path(conda).is_file():
        raise SystemExit('Install native arm64 Miniforge first. See README.md.')
    runtime = root / 'MuseTalk-Mac'
    if not runtime.exists():
        shutil.copytree(project / 'third_party/MuseTalk-Mac', runtime)
    elif not (runtime / 'upstream/scripts/inference.py').is_file():
        raise SystemExit('Existing runtime folder is different. It was not overwritten. Use a new --root.')
    muse = root / 'env-musetalk'
    if not muse.exists():
        run([conda, 'create', '-y', '-p', muse, 'python=3.11', 'ffmpeg'])
        run([muse / 'bin/python', '-m', 'pip', 'install', '--no-cache-dir', '-r', runtime / 'requirements-mac.txt',
             'torch==2.5.1', 'torchvision==0.20.1', 'torchaudio==2.5.1', 'opencv-contrib-python==4.9.0.80'])
    else:
        print('Keeping existing animation environment. Its dependencies were not changed.')
    heart = root / 'env-heart'
    if not heart.exists():
        run([muse / 'bin/python', '-m', 'venv', '--system-site-packages', heart])
        run([heart / 'bin/python', '-m', 'pip', 'install', '--no-cache-dir', '-r', project / 'heart-backend/requirements.txt'])
    else:
        print('Keeping existing voice environment. Its dependencies were not changed.')
    for source, target in [(project / 'liveportrait/aria-approved.png', root / 'aria-approved.png'),
                           (project / 'assets/aria-approved--d0.mp4', root / 'example-animation/aria-approved--d0.mp4')]:
        copy_if_missing(source, target)
    if args.usb.is_mount():
        destination = args.usb / 'ARIA-MuseTalk-Models'
        destination.mkdir(exist_ok=True)
        models = runtime / 'upstream/models'
        if not models.exists() and not models.is_symlink():
            models.symlink_to(destination)
        elif not models.is_symlink() or models.resolve() != destination.resolve():
            raise SystemExit('Existing model folder differs. No models were moved or overwritten.')
        if args.download_models:
            if shutil.disk_usage(args.usb).free < 5 * 1024**3:
                raise SystemExit('Model downloads need more free space on the USB.')
            run([conda, 'run', '--no-capture-output', '-p', muse, 'bash', runtime / 'download_weights_mac.sh'])
    elif args.download_models:
        raise SystemExit('USB is not mounted. No model download started.')
    else:
        print('USB not mounted. Voice-only mode can work; lip-sync needs the configured models and USB.')
    run([heart / 'bin/python', '-c', 'from kokoro import KPipeline; from misaki.espeak import EspeakFallback; print("Voice imports passed")'])
    print('Environment preparation finished. Start launch_aria.command. Render a short reply to verify this installation.')


if __name__ == '__main__':
    main()
