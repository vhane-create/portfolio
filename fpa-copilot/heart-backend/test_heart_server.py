import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from http.server import ThreadingHTTPServer
import numpy as np

spec=importlib.util.spec_from_file_location('heart_server',Path(__file__).with_name('heart_server.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class Array:
    def detach(self): return self
    def cpu(self): return self
    def numpy(self): return np.sin(np.arange(2400)*0.1).astype('float32')*0.1

class Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.project=self.root/'project';self.project.mkdir()
        source=b'<html><body><video id="aria-heart-video"></video></body></html>'
        (self.project/'aria-heart-preview.html').write_bytes(source)
        self.before=source
        (self.project/'secret.env').write_text('private')
        self.app=module.App(self.project,self.root,lambda text,voice:[(None,None,Array())])
        self.server=ThreadingHTTPServer(('127.0.0.1',0),module.handler_for(self.app))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.app.pool.shutdown();self.temp.cleanup()
    def request(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        conn.request(method,path,body,headers or {})
        response=conn.getresponse();result=(response.status,response.read());conn.close();return result
    def test_page_and_preservation(self):
        status,body=self.request('GET','/')
        self.assertEqual(status,200)
        self.assertIn(b'Heart with lip sync (slower)',body)
        self.assertEqual((self.project/'aria-heart-preview.html').read_bytes(),self.before)
    def test_audio_job_and_playable_wav_transport(self):
        status,body=self.request('POST','/api/reply',json.dumps({'text':'Twenty percent variance.','kind':'audio'}),{'Content-Type':'application/json'})
        self.assertEqual(status,202)
        identity=json.loads(body)['id']
        for _ in range(100):
            _,body=self.request('GET','/api/job/'+identity)
            job=json.loads(body)
            if job['state'] not in ('speaking','rendering'):break
            time.sleep(.02)
        self.assertEqual(job['state'],'ready',job)
        status,body=self.request('GET',job['url'])
        self.assertEqual(status,200);self.assertEqual(body[:4],b'RIFF')
        self.assertNotIn('path',job)
    def test_input_rejections(self):
        for data in [{'text':'','kind':'audio'},{'text':'x','kind':'other'},['invalid']]:
            status,_=self.request('POST','/api/reply',json.dumps(data),{'Content-Type':'application/json'})
            self.assertEqual(status,400)
    def test_origin_and_private_file_rejections(self):
        self.assertEqual(self.request('GET','/',headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('POST','/api/reply','{}',{'Origin':'https://evil.example','Content-Type':'application/json'})[0],403)
        for path in ['/secret.env','/../secret.env','/.git/config','/api/media/nope.mp4']:
            self.assertEqual(self.request('GET',path)[0],404)
    def test_render_failure_reported(self):
        with patch.object(self.app,'render',side_effect=RuntimeError('USB not connected')):
            identity=self.app.submit('Test','video')
            for _ in range(100):
                if self.app.jobs[identity]['state']=='error':break
                time.sleep(.02)
            self.assertEqual(self.app.jobs[identity]['state'],'error')
            self.assertIn('USB',self.app.jobs[identity]['error'])
    def test_reject_simultaneous_generation(self):
        self.app.jobs['busy']={'state':'rendering'}
        with self.assertRaises(RuntimeError):self.app.submit('Test','audio')
    def test_rejects_changed_facial_source(self):
        (self.project/'assets').mkdir()
        (self.project/'assets/aria-approved--d0.mp4').write_bytes(b'different avatar')
        with self.assertRaisesRegex(RuntimeError,'approved animation'):
            self.app.render('test',self.root/'test.wav')
    def test_lazy_pipeline_still_uses_heart(self):
        calls=[]
        self.app.pipeline=None
        self.app.pipeline_factory=lambda:lambda text,voice:(calls.append((text,voice)) or [(None,None,Array())])
        identity=self.app.submit('A new answer.','audio')
        for _ in range(100):
            if self.app.jobs[identity]['state'] in ('ready','error'):break
            time.sleep(.02)
        self.assertEqual(self.app.jobs[identity]['state'],'ready')
        self.assertEqual(calls,[('A new answer.','af_heart')])

    def test_cached_route_reuses_client_and_keeps_media_validation(self):
        usb=self.root/'usb';usb.mkdir()
        work=self.root/'MuseTalk-Mac/upstream'
        (work/'models/musetalkV15').mkdir(parents=True)
        (work/'models/musetalkV15/unet.pth').write_bytes(b'fixture')
        (self.project/'assets').mkdir()
        approved=Path(__file__).resolve().parents[1]/'assets/aria-approved--d0.mp4'
        (self.project/'assets/aria-approved--d0.mp4').write_bytes(approved.read_bytes())
        calls=[]
        class Client:
            def render(inner,identity):
                calls.append(identity)
                (usb/'ARIA-Live-Replies'/(identity+'.mp4')).write_bytes(b'fixture video')
        self.app.cached_renderer=Client()
        result=SimpleNamespace(returncode=0,stdout=json.dumps({'streams':[{'codec_type':'audio'},{'codec_type':'video'}]}))
        with patch.dict(module.os.environ,{'ARIA_USB':str(usb),'ARIA_CACHED_RENDERER':'1'}),patch.object(Path,'is_mount',return_value=True),patch.object(module.subprocess,'run',return_value=result) as run:
            for identity in ('a'*32,'b'*32):
                self.assertEqual(self.app.render(identity,self.root/'test.wav').name,identity+'.mp4')
        self.assertEqual(calls,['a'*32,'b'*32])
        self.assertEqual(run.call_count,4)
        self.assertTrue(all(call.args[0][0].endswith(('ffprobe','ffmpeg')) for call in run.call_args_list))

if __name__=='__main__':unittest.main()
