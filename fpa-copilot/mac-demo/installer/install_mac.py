"""Install a pinned, small ARIA Mac demo into its own directory and launch it."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import Request, urlopen

REVISION = '641a211b0a2f79b1160543ea38443b39ec51d8b2'
MANIFEST = {
  "aria-final.html": {
    "sha": "243acb39a302831a1724942ded058376e7098c2a",
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
  "assets/aria-full-body-approved.png": {
    "sha": "31197d446c9fb52b741b8d91f7ceebed7ec35a89",
    "size": 1853535
  },
  "conversation.js": {
    "sha": "342aab465b05f07fc092befdfd00ef42464aad23",
    "size": 6755
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
    "sha": "838531c7cf60994b5dfd11ed3c57bea1951a2dde",
    "size": 4956
  },
  "mac-demo/Start_ARIA_Mac.command": {
    "sha": "605b2519e82b7b009d54d2c92e71b057d0dd9ac2",
    "size": 297
  },
  "mac-demo/server.py": {
    "sha": "4d5a6ec02ae2dc0965a753059653949acc5c8606",
    "size": 10000
  },
  "mac-demo/status.js": {
    "sha": "dbd69017ece12e2f0d48dade486411df8e07ff3f",
    "size": 893
  },
  "voice-loop.js": {
    "sha": "e6c4dfa3d63a18c4a0a354c61cc83de6d7c94996",
    "size": 8643
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
    print('Downloading about 4.9 MB of demo files. Voice/model downloads are separate.', flush=True)
    install(root)
    launcher = root / 'mac-demo/Start_ARIA_Mac.command'
    launcher.chmod(0o700)
    print('\nSaved to: ' + str(root), flush=True)
    print('In LM Studio: load a chat model, then start the local server on port 1234.', flush=True)
    print('No paid hosting, public tunnel, or animation-model download is enabled.', flush=True)
    subprocess.run(['open', '-a', 'LM Studio'], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.execv(sys.executable, [sys.executable, str(root / 'mac-demo/server.py')])


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        print('\nARIA setup stopped: ' + str(error), file=sys.stderr)
        input('Press Return to close. ')
        raise SystemExit(1)
