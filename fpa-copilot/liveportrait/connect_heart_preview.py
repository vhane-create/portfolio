from pathlib import Path
import re
import sys

project = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / 'ARIA-Setup/fpa-copilot'
source = project / 'aria-live.html'
output = project / 'aria-heart-preview.html'
for file in [source, project / 'assets/ARIA_Heart_Introduction.mp4', project / 'liveportrait/aria-approved.png']:
    if not file.is_file() or file.stat().st_size == 0:
        raise SystemExit(f'Stopped: required file missing or empty: {file}')
if output.exists():
    raise SystemExit('Preview already exists. Nothing was overwritten.')
html = source.read_text()
for marker in ['id="screen"', 'id="intro"', 'id="stop"', 'function say(t)', '</body>']:
    if marker not in html:
        raise SystemExit(f'Stopped: existing page differs: {marker}')
html = html.replace('This is a still portrait with a voice interface, not a lip-synchronized video avatar.', 'The introduction uses ARIA’s approved Heart voice and lip-synchronized video. Other answers are currently text only.')
html = html.replace('Voice playback depends on your browser. This is a spoken demonstration, not a lip-synchronized avatar.', 'These topics currently return text. Heart voice and lip synchronization are available for the introduction.')
html = html.replace('Browser voice availability varies.', 'Heart voice is connected to the introduction; other replies are text only.')
extra = '''<style>#aria-heart-video{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.overlay{z-index:2}</style>
<script>
(()=>{
const screen=document.getElementById('screen');
const portrait=screen.querySelector('img');
if(!portrait)throw Error('ARIA portrait element missing');
const video=document.createElement('video');
video.id='aria-heart-video';video.src='assets/ARIA_Heart_Introduction.mp4';
video.poster='liveportrait/aria-approved.png';video.preload='metadata';video.playsInline=true;
video.setAttribute('aria-label','ARIA, a Black female android with long wavy black hair and a black executive suit');
portrait.replaceWith(video);
document.getElementById('missing').hidden=true;
say=function(){video.pause();screen.dataset.state='idle';status('Text reply ready — Heart introduction available');};
const intro=document.getElementById('intro');intro.textContent='Play introduction';
intro.onclick=async()=>{synth?.cancel();video.currentTime=0;try{await video.play();}catch(e){status('Unable to play introduction. Check the video file.');}};
video.onplay=()=>{screen.dataset.state='speaking';status('Speaking with Heart');};
video.onended=()=>{screen.dataset.state='idle';status('Ready');};
video.onerror=()=>{status('Introduction video could not load');};
const mute=document.getElementById('mute');
mute.textContent='Introduction audio: on';
mute.onclick=()=>{video.muted=!video.muted;mute.textContent=video.muted?'Introduction audio: off':'Introduction audio: on';mute.setAttribute('aria-pressed',String(video.muted));};
document.getElementById('stop').onclick=()=>{video.pause();video.currentTime=0;synth?.cancel();recognizer?.stop();screen.dataset.state='idle';status('Stopped');};
document.getElementById('clear').addEventListener('click',()=>{video.pause();screen.dataset.state='idle';});
})();
</script>'''
html=html.replace('</body>',extra+'</body>')
with output.open('x') as file:
    file.write(html)
print('DONE: aria-heart-preview.html created. Existing pages kept intact.')
