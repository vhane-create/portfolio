import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import render_worker
from cached_renderer import CachedRenderer


class WorkerTests(unittest.TestCase):
    def fixture(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name)
        source=root/'source.mp4';source.write_bytes(b'approved fixture')
        audio=root/'audio';audio.mkdir();output=root/'out';output.mkdir()
        return root,source,audio,output

    def test_two_replies_initialize_once_and_preserve_pairing(self):
        root,source,audio,out=self.fixture();ids=['a'*32,'b'*32];calls=[]
        for identity in ids:(audio/(identity+'.wav')).write_bytes(identity.encode())
        class Engine:
            @staticmethod
            def initialize(upstream,src):calls.append('initialize');return object()
            @staticmethod
            def render(avatar,wav):calls.append(('render',id(avatar)));return b'video:'+wav.read_bytes()
        incoming=io.StringIO(''.join(json.dumps({'id':x})+'\n' for x in ids));result=io.StringIO()
        with patch.object(render_worker,'APPROVED_SHA',hashlib.sha256(source.read_bytes()).hexdigest()):
            self.assertEqual(render_worker.serve(incoming,result,root,source,audio,out,Engine),0)
        self.assertEqual(calls[0],'initialize');self.assertEqual(len(calls),3)
        self.assertEqual(calls[1],calls[2])
        self.assertEqual([json.loads(x)['id'] for x in result.getvalue().splitlines()],ids)
        for identity in ids:self.assertEqual((out/(identity+'.mp4')).read_bytes(),b'video:'+identity.encode())

    def test_changed_source_stops_before_model_loading(self):
        root,source,audio,out=self.fixture();result=io.StringIO()
        self.assertEqual(render_worker.serve(io.StringIO(json.dumps({'id':'a'*32})+'\n'),result,root,source,audio,out,object()),1)
        self.assertIn('source differs',json.loads(result.getvalue())['error'])
        self.assertEqual(list(out.iterdir()),[])

    def test_existing_output_and_audio_escape_are_rejected(self):
        for escape in (False,True):
            with self.subTest(escape=escape):
                root,source,audio,out=self.fixture();identity='a'*32
                if escape:
                    outside=root/'private.wav';outside.write_bytes(b'private')
                    (audio/(identity+'.wav')).symlink_to(outside)
                else:
                    (audio/(identity+'.wav')).write_bytes(b'audio')
                    (out/(identity+'.mp4')).write_bytes(b'keep')
                result=io.StringIO()
                with patch.object(render_worker,'APPROVED_SHA',hashlib.sha256(source.read_bytes()).hexdigest()):
                    self.assertEqual(render_worker.serve(io.StringIO(json.dumps({'id':identity})+'\n'),result,root,source,audio,out,object()),1)
                self.assertFalse(json.loads(result.getvalue())['ok'])
                if not escape:self.assertEqual((out/(identity+'.mp4')).read_bytes(),b'keep')


class ProcessTests(unittest.TestCase):
    def fixture(self,body):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);root=Path(temp.name)
        script=root/'worker.py';script.write_text(body)
        client=CachedRenderer([sys.executable,'-u',str(script)],root,os.environ.copy(),root/'worker.log')
        self.addCleanup(client.close);return client

    def test_two_requests_reuse_real_subprocess(self):
        client=self.fixture("import sys,json\nfor line in sys.stdin:\n d=json.loads(line);print(json.dumps({'id':d['id'],'ok':True}),flush=True)\n")
        client.render('a'*32,timeout=2);pid=client.process.pid
        client.render('b'*32,timeout=2);self.assertEqual(client.process.pid,pid)

    def test_timeout_terminates_worker(self):
        client=self.fixture('import time\ntime.sleep(10)\n')
        with self.assertRaisesRegex(RuntimeError,'timed out'):client.render('a'*32,timeout=.1)
        self.assertIsNone(client.process)

    def test_wrong_reply_is_rejected_and_worker_closed(self):
        client=self.fixture("import sys,json\nfor line in sys.stdin: print(json.dumps({'id':'wrong','ok':True}),flush=True)\n")
        with self.assertRaisesRegex(RuntimeError,'different reply'):client.render('a'*32,timeout=2)
        self.assertIsNone(client.process)

    def test_exited_worker_restarts(self):
        client=self.fixture("import sys,json\nd=json.loads(sys.stdin.readline());print(json.dumps({'id':d['id'],'ok':True}),flush=True)\n")
        client.render('a'*32,timeout=2);pid=client.process.pid;client.process.wait(timeout=2)
        client.render('b'*32,timeout=2);self.assertNotEqual(client.process.pid,pid)


if __name__=='__main__':unittest.main()
