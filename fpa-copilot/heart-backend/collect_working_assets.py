"""Collect only ARIA project assets and code; never remove or change originals."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import re
import zipfile

root = Path.home() / 'ARIA-LivePortrait'
project = Path.home() / 'ARIA-Setup/fpa-copilot'
usb = Path('/Volumes/NO NAME')
output = Path.home() / 'Desktop/ARIA_Working_Assets.zip'
portrait = root / 'aria-approved.png'
expected = '9889d86d17f07437243204107a91ed7ab4a49a5a9d1841ec56c59d117247d958'

required = {
    'fpa-copilot/liveportrait/aria-approved.png': portrait,
    'fpa-copilot/assets/ARIA_Heart_Introduction.mp4': project / 'assets/ARIA_Heart_Introduction.mp4',
    'fpa-copilot/assets/aria-heart-intro.wav': root / 'aria-heart-intro.wav',
    'fpa-copilot/assets/aria-approved--d0.mp4': root / 'example-animation/aria-approved--d0.mp4',
    'fpa-copilot/aria-heart-preview.html': project / 'aria-heart-preview.html',
    'fpa-copilot/heart-backend/heart_server.py': project / 'heart-backend/heart_server.py',
    'fpa-copilot/working-runtime/musetalk/models/unet.py': root / 'MuseTalk-Mac/upstream/musetalk/models/unet.py',
    'fpa-copilot/working-runtime/musetalk/models/vae.py': root / 'MuseTalk-Mac/upstream/musetalk/models/vae.py',
    'fpa-copilot/working-runtime/musetalk/utils/utils.py': root / 'MuseTalk-Mac/upstream/musetalk/utils/utils.py',
}
if output.exists():
    raise SystemExit('Collection already exists on Desktop. Nothing overwritten.')
for name, file in required.items():
    if not file.is_file() or file.stat().st_size == 0:
        raise SystemExit('Stopped: required ARIA file missing or empty: ' + str(file))
if hashlib.sha256(portrait.read_bytes()).hexdigest() != expected:
    raise SystemExit('Stopped: portrait does not match the exact approved ARIA image.')

replies = sorted((usb / 'ARIA-Live-Replies').glob('*/v15/*.mp4'))
replies = [p for p in replies if re.fullmatch(r'[0-9a-f]{32}', p.stem) and p.stat().st_size > 0]
if not replies:
    raise SystemExit('Stopped: completed conversational reply video not found. Keep the USB connected.')
latest = max(replies, key=lambda p: p.stat().st_mtime)
required['fpa-copilot/assets/ARIA_Variance_Reply.mp4'] = latest
wav = root / 'heart-replies' / (latest.stem + '.wav')
if wav.is_file():
    required['fpa-copilot/assets/ARIA_Variance_Reply.wav'] = wav
test = root / 'aria-heart-reply-test.wav'
if test.is_file():
    required['fpa-copilot/assets/aria-heart-reply-test.wav'] = test
for name in ('README.md', 'requirements.txt', 'test_heart_server.py'):
    file = project / 'heart-backend' / name
    if file.is_file():
        required['fpa-copilot/heart-backend/' + name] = file

manifest = {'portrait_sha256': expected, 'voice': 'af_heart', 'voice_engine': 'Kokoro',
            'sample_rate': 24000, 'user_confirmed': ['approved appearance', 'Heart voice', 'introduction lip sync', 'new finance reply lip sync', 'variance 20000 and 20 percent'],
            'limitations': ['new animated replies require local Python and USB', 'rendering takes minutes', 'public dynamic backend not deployed', 'blinking not separately reviewed'],
            'files': {name: {'bytes': file.stat().st_size, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()} for name, file in required.items()}}
packages = {}
for package in ('kokoro', 'misaki', 'spacy', 'numpy', 'torch', 'transformers', 'huggingface-hub', 'soundfile'):
    try:
        packages[package] = importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        packages[package] = 'not found in collection environment'
manifest['voice_environment_versions'] = packages
with zipfile.ZipFile(output, mode='x', compression=zipfile.ZIP_DEFLATED) as archive:
    for name, file in required.items():
        archive.write(file, name)
    archive.writestr('fpa-copilot/WORKING_ASSETS_MANIFEST.json', json.dumps(manifest, indent=2))
with zipfile.ZipFile(output) as archive:
    failed = archive.testzip()
if failed:
    raise SystemExit('Archive verification failed: ' + failed)
print('DONE: verified ARIA_Working_Assets.zip saved on Desktop. Originals kept intact.')
import subprocess
subprocess.run(['open', '-R', str(output)], check=True)
