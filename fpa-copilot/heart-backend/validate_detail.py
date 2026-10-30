"""Offline detail comparison for an existing approved-source render; not live speech."""
from pathlib import Path
import sys,subprocess,json,argparse,hashlib
import cv2,numpy as np
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project',type=Path,default=Path(__file__).resolve().parents[1])
parser.add_argument('--render',type=Path,required=True)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
project=args.project.resolve();root=args.output_dir.resolve();render_path=args.render.resolve()
root.mkdir(parents=True,exist_ok=True)
for name in ('ARIA_Detail_Check.mp4','detail-silent.mp4','detail-comparison.png','detail-report.json'):
 if (root/name).exists(): raise SystemExit('Use a new output directory; existing files were kept.')
if hashlib.sha256((project/'assets/aria-approved--d0.mp4').read_bytes()).hexdigest()!='308ab080d0945bb650f905174e716a8a5beecb9b26ec56590aa1aa8ac72839b7':
 raise SystemExit('Approved source differs; stopped.')
sys.path.insert(0,str(project/'heart-backend'))
from mouth_detail import DetailBlender
out=root/'ARIA_Detail_Check.mp4';silent=out.with_name('detail-silent.mp4')
source=cv2.VideoCapture(str(project/'assets/aria-approved--d0.mp4'));render=cv2.VideoCapture(str(render_path))
if not source.isOpened() or not render.isOpened(): raise SystemExit('Both source and render must decode.')
expected=int(render.get(cv2.CAP_PROP_FRAME_COUNT))
if expected<1 or expected>int(source.get(cv2.CAP_PROP_FRAME_COUNT)) or abs(source.get(cv2.CAP_PROP_FPS)-render.get(cv2.CAP_PROP_FPS))>.01:
 raise SystemExit('This offline check requires matching frame rates and a render no longer than one source cycle.')
blender=DetailBlender();frames=0;unchanged=True;tiles=[];stats=[]
writer=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','852x1280','-r','25','-i','-','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE)
while True:
 ok,a=source.read();ok2,b=render.read()
 if not(ok and ok2):break
 c,alpha=blender.blend(a,b,frames)
 unchanged &= bool(np.array_equal(a[alpha==0],c[alpha==0]))
 stats.append(float((alpha>0).mean()))
 writer.stdin.write(c.tobytes())
 if frames in (0,12,25,38,50,66,74):
  crop=lambda x:x[95:340,290:535]
  tile=np.concatenate([crop(a),crop(b),crop(c)],axis=1)
  cv2.putText(tile,str(frames),(5,20),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,255,0),1);tiles.append(tile)
 frames+=1
writer.stdin.close();assert writer.wait()==0;blender.close();source.release();render.release()
if frames!=expected: raise RuntimeError('Render stopped before all expected frames decoded.')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(render_path),'-map','0:v:0','-map','1:a:0','-c','copy','-shortest',str(out)],check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
cv2.imwrite(str(root/'detail-comparison.png'),np.concatenate(tiles,axis=0))
report={'frames':frames,'outside_mouth_support_exact_before_encoding':unchanged,'mean_frame_fraction_affected':float(np.mean(stats)),'scope':'Compositing pass on completed render using existing Heart audio. Not new speech or a live conversation. Subjective seams and lip timing need review.'}
(root/'detail-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
