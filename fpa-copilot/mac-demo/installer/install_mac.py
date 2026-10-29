"""Install a pinned, small ARIA Mac demo into its own directory and launch it."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import Request, urlopen

REVISION = '4172172131214a98bfbe677f16565a177a668a59'
MANIFEST = {
  "aria-final.html": {
    "sha": "2abe869e67ce96c86b0f29e606a9b37304d6e692",
    "size": 29643
  },
  "assets/ARIA_Heart_Introduction.mp4": {
    "sha": "5181a0a3becf9d840222c12761ab57b130c78b39",
    "size": 240357
  },
  "assets/ARIA_Variance_Reply.mp4": {
    "sha": "0fe418dfae4b10a29e714885c97fa5469cf7ebca",
    "size": 684040
  },
  "assets/aria-approved--d0.mp4": {
    "sha": "68d65747926d9b3184009f676e1598e05568f7cb",
    "size": 263178
  },
  "assets/aria-full-body-approved.png": {
    "sha": "31197d446c9fb52b741b8d91f7ceebed7ec35a89",
    "size": 1853535
  },
  "conversation.js": {
    "sha": "342aab465b05f07fc092befdfd00ef42464aad23",
    "size": 6755
  },
  "heart-backend/heart_server.py": {
    "sha": "264c73b9b358af5e626439184c1998f19fefff94",
    "size": 16025
  },
  "heart-worker.js": {
    "sha": "7c156539b870f28c1d63ad00d497378fe59c19b0",
    "size": 3188
  },
  "immersive.css": {
    "sha": "4ea91f4faa6d51a83106831def324d44161d2b90",
    "size": 4653
  },
  "immersive.js": {
    "sha": "04d45fbeb444d9dd40ca2616103f1d0c75ffc25e",
    "size": 3700
  },
  "liveportrait/aria-approved.png": {
    "sha": "65755fcda8aa9517d134154f87e0e5e170ee2d49",
    "size": 1981765
  },
  "mac-demo/README.md": {
    "sha": "21022585caf17b4dd4ee7251f520cda2842a6b39",
    "size": 6411
  },
  "mac-demo/Start_ARIA_Mac.command": {
    "sha": "e09f61297f7eeb480e5966f108db76c20a433e90",
    "size": 515
  },
  "mac-demo/face-replies.js": {
    "sha": "a809f43722c2ff6983d0b1ff93ed6d8eb39323f8",
    "size": 2835
  },
  "mac-demo/server.py": {
    "sha": "fc6822156480aaffcd15cfdd540f4bbae6f88bb9",
    "size": 14442
  },
  "mac-demo/status.js": {
    "sha": "8cd57277fca63ed241b88a840996ec6594a2f5f3",
    "size": 915
  },
  "voice-loop.js": {
    "sha": "bcfc63e1b7de752969e9c101bc7c2101c46d2eb5",
    "size": 10800
  }
}


def git_hash(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def install(root, manifest=MANIFEST, download=None):
    root = Path(root)
    downloaded = 0
    for name, expected in manifest.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Invalid package path.')
        target = root / relative
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
            raise ValueError('An install path is a symbolic link; existing files were kept.')
        if target.exists():
            current = target.read_bytes()
            if len(current) == expected['size'] and git_hash(current) == expected['sha']:
                continue
            raise ValueError('Existing file differs from the release; it was not overwritten: ' + str(target))
        url = f'https://raw.githubusercontent.com/vhane-create/portfolio/{REVISION}/fpa-copilot/{name}'
        print('Downloading ' + name, flush=True)
        if download:
            data = download(url, expected['size'])
        else:
            with urlopen(Request(url, headers={'User-Agent':'ARIA-Mac-Demo-Installer'}), timeout=60) as response:
                data = response.read(expected['size'] + 1)
        if len(data) != expected['size'] or git_hash(data) != expected['sha']:
            raise ValueError('Download did not match the reviewed release: ' + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation preserves any file created while the download ran.
        with target.open('xb') as output:
            output.write(data)
        downloaded += 1
    return downloaded


def main():
    if sys.platform != 'darwin':
        raise ValueError('Run this launcher on your Mac, not the remote test workspace.')
    if not MANIFEST:
        raise ValueError('Release manifest is missing.')
    root = Path.home() / 'ARIA-Mac-Demo' / 'releases' / REVISION / 'fpa-copilot'
    print('ARIA Mac demo — preserving her approved appearance and Heart voice.', flush=True)
    print('Downloading about 5.2 MB of demo files. Voice/model downloads are separate.', flush=True)
    install(root)
    launcher = root / 'mac-demo/Start_ARIA_Mac.command'
    launcher.chmod(0o700)
    print('\nSaved to: ' + str(root), flush=True)
    print('In LM Studio: load a chat model, then start the local server on port 1234.', flush=True)
    print('No paid hosting, public tunnel, or animation-model download is enabled.', flush=True)
    subprocess.run(['open', '-a', 'LM Studio'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    heart_python = Path(os.environ.get('ARIA_ROOT', str(Path.home() / 'ARIA-LivePortrait'))) / 'env-heart/bin/python'
    python = str(heart_python) if heart_python.is_file() and os.access(heart_python, os.X_OK) else sys.executable
    print('Starting with Python: ' + python, flush=True)
    os.execv(python, [python, str(root / 'mac-demo/server.py')])


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        print('\nARIA setup stopped: ' + str(error), file=sys.stderr)
        input('Press Return to close. ')
        raise SystemExit(1)
