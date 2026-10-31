"""Install the exact inspected source and verify the official model downloads.

Run in a fresh environment with muse_requirements.txt installed. Downloads
about 4 GB of weights. Does not install globally, purchase, or change the tour.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request

FORK='7fd019315127d7f31e2e7f9853547ddceabbeb6e'
UPSTREAM='0a89dec45a0192b824e3cf4daf96c239440c5ed8'
URLS={
 'models/musetalkV15/musetalk.json':'https://huggingface.co/TMElyralab/MuseTalk/resolve/main/musetalkV15/musetalk.json',
 'models/musetalkV15/unet.pth':'https://huggingface.co/TMElyralab/MuseTalk/resolve/main/musetalkV15/unet.pth',
 'models/sd-vae/config.json':'https://huggingface.co/stabilityai/sd-vae-ft-mse/resolve/main/config.json',
 'models/sd-vae/diffusion_pytorch_model.bin':'https://huggingface.co/stabilityai/sd-vae-ft-mse/resolve/main/diffusion_pytorch_model.bin',
 'models/whisper/config.json':'https://huggingface.co/openai/whisper-tiny/resolve/main/config.json',
 'models/whisper/pytorch_model.bin':'https://huggingface.co/openai/whisper-tiny/resolve/main/pytorch_model.bin',
 'models/whisper/preprocessor_config.json':'https://huggingface.co/openai/whisper-tiny/resolve/main/preprocessor_config.json',
 'models/face-parse-bisent/79999_iter.pth':'https://drive.usercontent.google.com/download?id=154JgKpzCPW82qINcVieuPH3fZ2e0P812&export=download&confirm=t',
 'models/face-parse-bisent/resnet18-5c106cde.pth':'https://download.pytorch.org/models/resnet18-5c106cde.pth',
}


def sha(path):
    digest=hashlib.sha256()
    with path.open('rb') as f:
        while block:=f.read(4*1024*1024):digest.update(block)
    return digest.hexdigest()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--directory',type=Path,default=Path('musetalk_engine'))
    a=p.parse_args()
    if shutil.disk_usage(Path.cwd()).free<8*1024**3:
        raise SystemExit('At least 8 GB of free disk space is required before setup.')
    if not a.directory.exists():
        subprocess.run(['git','clone','--no-checkout','https://github.com/barnent1/musetalk-mac.git',str(a.directory)],check=True)
        subprocess.run(['git','-C',str(a.directory),'checkout',FORK],check=True)
    else:
        head=subprocess.check_output(['git','-C',str(a.directory),'rev-parse','HEAD'],text=True).strip()
        if head!=FORK:raise SystemExit('An existing engine has a different revision; choose a fresh directory.')
    root=a.directory/'upstream'
    manifest=json.loads(Path(__file__).with_name('engine_weights_verified.json').read_text())
    urls=dict(URLS)
    for filename in ('vae.py','unet.py'):
        urls['musetalk/models/'+filename]=f'https://raw.githubusercontent.com/TMElyralab/MuseTalk/{UPSTREAM}/musetalk/models/{filename}'
    for name,url in urls.items():
        target=root/name
        expected=manifest.get(name)
        if target.exists():
            if expected and (target.stat().st_size!=expected['size'] or sha(target)!=expected['sha256']):
                raise SystemExit(f'Existing file did not verify: {name}. Choose a fresh directory.')
            print('Verified existing' if expected else 'Existing source',name,flush=True)
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        pending=target.with_name(target.name+'.download')
        with urllib.request.urlopen(url,timeout=90) as response,pending.open('wb') as output:
            while block:=response.read(4*1024*1024):output.write(block)
        if expected and (pending.stat().st_size!=expected['size'] or sha(pending)!=expected['sha256']):
            pending.unlink()
            raise SystemExit(f'Download did not verify: {name}')
        pending.replace(target)
        print('Downloaded and verified' if expected else 'Downloaded source',name,flush=True)
    print('Engine ready for an offline render. This is not a live avatar deployment.')


if __name__=='__main__':main()
