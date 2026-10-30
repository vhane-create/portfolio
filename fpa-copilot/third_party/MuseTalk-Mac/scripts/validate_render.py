"""Offline CPU smoke render using approved source and existing Heart audio.
Does not import the upstream HTTP server or its optional voice providers.
"""
from pathlib import Path
import ast,os,sys,time,json,glob,shutil,tempfile,subprocess,resource,argparse,hashlib
from types import SimpleNamespace
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[3])
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
project=args.project.resolve()
output_dir=args.output_dir.resolve()
output_dir.mkdir(parents=True,exist_ok=True)
source=project/'assets/aria-approved--d0.mp4'
if hashlib.sha256(source.read_bytes()).hexdigest() != '308ab080d0945bb650f905174e716a8a5beecb9b26ec56590aa1aa8ac72839b7':
 raise SystemExit('Approved facial source checksum differs; stopped.')
if any((output_dir/name).exists() for name in ('ARIA_Heart_Render_Check.mp4','heart-check.wav','render-report.json')):
 raise SystemExit('Use a new output directory; existing test files were kept.')
fork=project/'third_party/MuseTalk-Mac'
os.chdir(fork/'upstream');sys.path.insert(0,str(Path.cwd()))
import cv2,numpy as np,torch
from transformers import WhisperModel
from musetalk.models.vae import VAE
from musetalk.models.unet import UNet,PositionalEncoding
from musetalk.utils.audio_processor import AudioProcessor
from musetalk.utils.face_parsing import FaceParsing
from musetalk.utils.preprocessing import get_landmark_and_bbox,coord_placeholder
from musetalk.utils.blending import get_image_prepare_material,get_image_blending
from musetalk.utils.utils import datagen,get_video_fps
class HTTPException(Exception):
 def __init__(self,status_code,detail):super().__init__(detail)
torch.set_num_threads(4);cv2.setNumThreads(2)
start=time.monotonic()
print('Loading memory-mapped UNet on CPU',flush=True)
unet=UNet('./models/musetalkV15/musetalk.json','./models/musetalkV15/unet.pth',device=torch.device('cpu'))
counter=[0]
def progress_hook(module, args, output):
 counter[0]+=1
 if counter[0]%10==0: print('Rendered mouth frames',counter[0],flush=True)
unet.model.register_forward_hook(progress_hook)
print('Loading VAE, Whisper and face parser',flush=True)
vae=VAE(model_path='./models/sd-vae')
whisper=WhisperModel.from_pretrained('./models/whisper',local_files_only=True).eval().requires_grad_(False)
state=dict(device=torch.device('cpu'),unet=unet,vae=vae,pe=PositionalEncoding(),whisper=whisper,audio_processor=AudioProcessor('./models/whisper'),weight_dtype=torch.float32,timesteps=torch.tensor([0]),fp=FaceParsing(left_cheek_width=90,right_cheek_width=90))
EXTRA_MARGIN=10
safe={'_detect_media_kind','_write_input_media','prepare_avatar','run_lipsync'}
tree=ast.parse((fork/'server.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in safe],type_ignores=[]),str(fork/'server.py'),'exec'),globals())
print('Preparing approved source frames',flush=True)
encode=vae.get_latents_for_unet
prepared=[0]
def tracked_encode(crop):
 result=encode(crop)
 prepared[0]+=1
 if prepared[0]%10==0: print('Prepared source frames',prepared[0],flush=True)
 return result
vae.get_latents_for_unet=tracked_encode
avatar=prepare_avatar(source.read_bytes())
print('Rendering existing Heart audio test segment',flush=True)
out=output_dir/'ARIA_Heart_Render_Check.mp4'
wav=output_dir/'heart-check.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(project/'assets/aria-heart-intro.wav'),'-t','3','-ar','24000','-ac','1',str(wav)],check=True)
with torch.inference_mode(): data=run_lipsync(avatar,wav.read_bytes(),batch_size=1)
out.write_bytes(data)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
report=dict(result='rendered_and_decoded',audio='First 3 seconds of included Heart introduction, not newly synthesized speech',video=str(out),elapsed_seconds=round(time.monotonic()-start,2),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitations=['Linux CPU, not Mac performance','Not a live conversation test','Blink quality not validated'])
(output_dir/'render-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
