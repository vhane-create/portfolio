"""Local ARIA Heart speech and MuseTalk reply renderer. Never hosted by GitHub Pages."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import io
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import threading
import uuid
import webbrowser

CLIENT = r'''
<script>
(()=>{
const video=document.getElementById('aria-heart-video');
const introURL=video.src;
const controls=document.querySelector('.overlay .actions');
const label=document.createElement('label');
label.textContent='Reply playback: ';
const select=document.createElement('select');
select.setAttribute('aria-label','Reply playback');
for(const [value,title] of [['video','Heart with lip sync (slower)'],['audio','Heart audio only (faster)']]){
 const option=document.createElement('option');option.value=value;option.textContent=title;select.append(option);
}
label.append(select);controls.append(label);
const audio=new Audio();let version=0,controller=null,muted=false,currentURL=null;
const screen=document.getElementById('screen');
function stopReply(){version++;controller?.abort();controller=null;audio.pause();video.pause();screen.dataset.state='idle';}
say=async function(text){
 stopReply();const own=version;const kind=select.value;
 if(muted){status('Text reply ready — audio muted');return;}
 controller=new AbortController();status('Generating Heart voice…');screen.dataset.state='generating';
 try{
  const response=await fetch('/api/reply',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,kind}),signal:controller.signal});
  const started=await response.json();if(!response.ok)throw Error(started.error||'Voice service unavailable');
  for(;;){
   if(own!==version)return;
   const poll=await fetch('/api/job/'+started.id,{signal:controller.signal});
   if(!poll.ok)throw Error('Unable to check reply');
   const job=await poll.json();
   if(job.state==='error')throw Error(job.error);
   if(job.state==='ready'){
    if(own!==version)return;
    currentURL=job.url;
    if(kind==='video'){video.src=job.url;video.muted=false;await video.play();}
    else{video.load();audio.src=job.url;await audio.play();screen.dataset.state='speaking';status('Speaking with Heart — audio only');}
    break;
   }
   status(job.state==='rendering'?'Rendering matching lip movements — please wait…':'Generating Heart voice…');
   await new Promise(resolve=>setTimeout(resolve,1500));
  }
 }catch(error){if(own===version&&error.name!=='AbortError'){screen.dataset.state='idle';status(error.name==='NotAllowedError'?'Reply ready — click Play latest reply':'Reply unavailable: '+error.message);}}
};
audio.onended=()=>{screen.dataset.state='idle';status('Ready');};
audio.onerror=()=>status('Reply audio could not play');
const replay=document.createElement('button');replay.textContent='Play latest reply';controls.append(replay);
replay.onclick=async()=>{if(!currentURL){status('Ask a question first');return;}try{if(currentURL.endsWith('.mp4')){video.src=currentURL;await video.play();}else{audio.src=currentURL;await audio.play();}}catch(e){status('Unable to play reply');}};
document.getElementById('intro').onclick=async()=>{stopReply();video.src=introURL;video.muted=muted;try{await video.play();}catch(e){status('Introduction could not play');}};
const mute=document.getElementById('mute');mute.textContent='Voice: on';
mute.onclick=()=>{muted=!muted;audio.muted=muted;video.muted=muted;mute.textContent=muted?'Voice: off':'Voice: on';mute.setAttribute('aria-pressed',String(muted));};
document.getElementById('stop').onclick=()=>{stopReply();recognizer?.stop();status('Playback stopped; a render already running may finish in the background');};
document.getElementById('clear').addEventListener('click',stopReply);
status('Heart connected — lip-synced replies selected');
})();
</script>
'''


def make_page(project):
    source = project / 'aria-heart-preview.html'
    text = source.read_text()
    if 'aria-heart-video' not in text or '</body>' not in text:
        raise ValueError('Existing Heart preview is different; no files changed.')
    text = text.replace('Other answers are currently text only.', 'New answers use Heart. Lip-synced replies render before playback and can take several minutes.')
    text = text.replace('These topics currently return text. Heart voice and lip synchronization are available for the introduction.', 'Choose a topic for a Heart response. Lip-sync mode takes longer; audio-only mode has no matching mouth animation.')
    text = text.replace('Heart voice is connected to the introduction; other replies are text only.', 'Local Heart and animation service must remain running. GitHub Pages alone cannot generate new voice or animation.')
    text = text.replace('The website remains available without your MacBook running.', 'This local voice session requires your MacBook and USB.')
    return text.replace('</body>', CLIENT + '</body>').encode()


class App:
    def __init__(self, project, root, pipeline=None, page=None, pipeline_factory=None):
        self.project, self.root, self.pipeline = project, root, pipeline
        self.pipeline_factory = pipeline_factory
        self.cached_renderer = None
        self.page = make_page(project) if page is None else page
        self.cache = root / 'heart-replies'
        self.cache.mkdir(exist_ok=True)
        self.jobs = {}
        self.lock = threading.Lock()
        self.pool = ThreadPoolExecutor(max_workers=1)

    def submit(self, text, kind):
        if not isinstance(text, str) or not text.strip() or len(text) > 6000:
            raise ValueError('Reply must contain 1 to 6000 characters.')
        if kind not in ('audio', 'video'):
            raise ValueError('Unknown reply mode.')
        with self.lock:
            if any(j['state'] in ('speaking', 'rendering') for j in self.jobs.values()):
                raise RuntimeError('One reply is still being generated. Please wait for it to finish.')
            identity = uuid.uuid4().hex
            self.jobs[identity] = {'state': 'speaking', 'kind': kind}
        self.pool.submit(self.generate, identity, text, kind)
        return identity

    def generate(self, identity, text, kind):
        try:
            if shutil.disk_usage(self.root).free < 4 * 1024**3:
                raise RuntimeError('Less than 4 GB free on the internal drive. Generation stopped.')
            import numpy as np
            import soundfile as sf
            if self.pipeline is None:
                if self.pipeline_factory is None:
                    raise RuntimeError('The local Heart runtime is not configured.')
                self.pipeline = self.pipeline_factory()
            parts = [a.detach().cpu().numpy() for _, _, a in self.pipeline(text, voice='af_heart')]
            if not parts:
                raise RuntimeError('Heart generated no audio.')
            waveform = np.concatenate(parts)
            if not waveform.size or not np.isfinite(waveform).all() or not np.any(waveform):
                raise RuntimeError('Heart audio validation failed.')
            wav = self.cache / (identity + '.wav')
            with wav.open('xb') as handle:
                sf.write(handle, waveform, 24000, format='WAV', subtype='PCM_16')
            media = wav
            if kind == 'video':
                self.jobs[identity]['state'] = 'rendering'
                media = self.render(identity, wav)
            self.jobs[identity].update(state='ready', path=str(media), url='/api/media/' + identity + media.suffix)
        except Exception as error:
            self.jobs[identity].update(state='error', error=str(error))
            print('Reply failed:', error, flush=True)

    def render(self, identity, wav):
        usb = Path(os.environ.get('ARIA_USB', '/Volumes/NO NAME'))
        work = self.root / 'MuseTalk-Mac/upstream'
        source = self.project / 'assets/aria-approved--d0.mp4'
        if source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() != '308ab080d0945bb650f905174e716a8a5beecb9b26ec56590aa1aa8ac72839b7':
            raise RuntimeError('The facial-motion source differs from ARIA’s approved animation.')
        if not usb.is_mount() or not (work / 'models/musetalkV15/unet.pth').is_file() or not source.is_file():
            raise RuntimeError('Connect the USB with ARIA models and the approved source animation.')
        if shutil.disk_usage(usb).free < 1024**3:
            raise RuntimeError('Less than 1 GB free on the USB. Render stopped.')
        destination = usb / 'ARIA-Live-Replies'
        destination.mkdir(exist_ok=True)
        link = work / 'aria-live-results'
        if not link.exists() and not link.is_symlink():
            link.symlink_to(destination)
        if not link.is_symlink() or link.resolve() != destination.resolve():
            raise RuntimeError('Output folder conflict. Existing files were not changed.')
        configs = work / 'aria-live-configs'
        configs.mkdir(exist_ok=True)
        config = configs / (identity + '.json')
        config.write_text(json.dumps({'aria': {'video_path': str(source), 'audio_path': str(wav), 'result_name': identity + '.mp4'}}))
        env = os.environ.copy()
        binary = self.root / 'env-musetalk/bin'
        env.update(PYTORCH_ENABLE_MPS_FALLBACK='1', PYTORCH_MPS_HIGH_WATERMARK_RATIO='0.7', PYTORCH_MPS_LOW_WATERMARK_RATIO='0.5', PATH=str(binary) + os.pathsep + env.get('PATH', ''))
        if os.environ.get('ARIA_CACHED_RENDERER') == '1':
            # Opt-in until this runtime has completed an actual warm Mac test.
            if self.cached_renderer is None:
                import importlib.util
                backend = Path(__file__).resolve().parent
                spec = importlib.util.spec_from_file_location('aria_cached_renderer', backend / 'cached_renderer.py')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                command = [str(binary / 'python'), '-u', str(backend / 'render_worker.py'),
                           '--upstream', str(work.resolve()), '--source', str(source.resolve()),
                           '--audio-dir', str(self.cache.resolve()), '--output-dir', str(destination.resolve())]
                self.cached_renderer = module.CachedRenderer(command, work, env, self.cache / 'cached-renderer.log')
            self.cached_renderer.render(identity)
            output = destination / (identity + '.mp4')
            log = self.cache / 'cached-renderer.log'
            successful = True
        else:
            args = [str(binary / 'python'), '-m', 'scripts.inference', '--inference_config', './aria-live-configs/' + config.name,
                    '--result_dir', './aria-live-results/' + identity, '--unet_model_path', './models/musetalkV15/unet.pth',
                    '--unet_config', './models/musetalkV15/musetalk.json', '--whisper_dir', './models/whisper',
                    '--version', 'v15', '--batch_size', '1', '--use_float16']
            log = self.cache / (identity + '.log')
            with log.open('x') as handle:
                run = subprocess.run(args, cwd=work, env=env, stdout=handle, stderr=subprocess.STDOUT, timeout=3600)
            output = destination / identity / 'v15' / (identity + '.mp4')
            successful = run.returncode == 0
        if not successful or not output.is_file() or not output.stat().st_size:
            raise RuntimeError('Animation did not complete. Diagnostic log: ' + str(log))
        probe = subprocess.run([str(binary / 'ffprobe'), '-v', 'error', '-show_streams', '-of', 'json', str(output)], capture_output=True, text=True, check=True)
        streams = json.loads(probe.stdout)['streams']
        if not {'audio', 'video'}.issubset({s.get('codec_type') for s in streams}):
            raise RuntimeError('Generated video is missing audio or video.')
        subprocess.run([str(binary / 'ffmpeg'), '-v', 'error', '-i', str(output), '-f', 'null', '-'], capture_output=True, check=True, timeout=120)
        return output


def handler_for(app):
    class Handler(BaseHTTPRequestHandler):
        def allowed(self):
            port = self.server.server_port
            hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
            return self.headers.get('Host') in hosts and self.headers.get('Origin', f'http://127.0.0.1:{port}') in {f'http://{h}' for h in hosts}

        def send(self, status, data, mime='application/json'):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(data)

        def json(self, code, value):
            self.send(code, json.dumps(value).encode())

        def do_GET(self):
            if not self.allowed():
                self.json(403, {'error': 'Local origin required.'}); return
            path = unquote(urlsplit(self.path).path)
            if path in ('/', '/aria-heart-talk.html'):
                self.send(200, app.page, 'text/html; charset=utf-8'); return
            if path.startswith('/api/job/'):
                job = app.jobs.get(path.removeprefix('/api/job/'))
                if job is None:
                    self.json(404, {'error': 'Unknown reply.'}); return
                self.json(200, {k: v for k, v in job.items() if k != 'path'}); return
            if path.startswith('/api/media/'):
                name = path.removeprefix('/api/media/')
                identity = name.split('.')[0]
                job = app.jobs.get(identity, {})
                file = Path(job['path']) if job.get('state') == 'ready' else None
                if file is None or name != identity + file.suffix:
                    self.json(404, {'error': 'Reply not ready.'}); return
            else:
                file = (app.project / path.lstrip('/')).resolve()
                if not file.is_relative_to(app.project.resolve()) or any(p.startswith('.') for p in Path(path).parts) or file.suffix.lower() not in {'.html', '.js', '.css', '.png', '.jpg', '.jpeg', '.mp4', '.wav', '.svg', '.ico'}:
                    self.json(404, {'error': 'File unavailable.'}); return
            if not file.is_file():
                self.json(404, {'error': 'File unavailable.'}); return
            self.send(200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or 'application/octet-stream')

        def do_POST(self):
            if not self.allowed():
                self.json(403, {'error': 'Local origin required.'}); return
            if self.path != '/api/reply':
                self.json(404, {'error': 'Unknown endpoint.'}); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length < 1 or length > 30000 or self.headers.get_content_type() != 'application/json':
                    raise ValueError('Expected a small JSON reply request.')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('Expected a JSON object.')
                identity = app.submit(data.get('text'), data.get('kind', 'video'))
                self.json(202, {'id': identity})
            except (ValueError, TypeError) as error:
                self.json(400, {'error': str(error)})
            except RuntimeError as error:
                self.json(409, {'error': str(error)})
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    root = Path(os.environ.get('ARIA_ROOT', str(Path.home() / 'ARIA-LivePortrait'))).expanduser()
    project = Path(os.environ.get('ARIA_PROJECT', str(Path(__file__).resolve().parents[1]))).expanduser()
    for file in [project / 'aria-heart-preview.html', project / 'assets/ARIA_Heart_Introduction.mp4', project / 'liveportrait/aria-approved.png']:
        if not file.is_file():
            raise SystemExit('Missing required project file: ' + str(file))
    import torch
    from kokoro import KPipeline
    torch.set_num_threads(2)
    print('Loading Heart voice on CPU…', flush=True)
    pipeline = KPipeline(lang_code='a', device='cpu', repo_id='hexgrad/Kokoro-82M')
    app = App(project, root, pipeline)
    server = ThreadingHTTPServer(('127.0.0.1', 8765), handler_for(app))
    print('READY: http://127.0.0.1:8765 — leave this Terminal window open.', flush=True)
    print('Lip-synced replies render before playing. Audio-only mode has no matching mouth animation.', flush=True)
    if not args.no_browser:
        webbrowser.open('http://127.0.0.1:8765')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping. Any render already running may need time to finish.', flush=True)
    finally:
        server.server_close()
        app.pool.shutdown(wait=True)


if __name__ == '__main__':
    main()
