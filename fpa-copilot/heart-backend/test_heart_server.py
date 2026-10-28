import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
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

if __name__=='__main__':unittest.main()
