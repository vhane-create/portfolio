from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from server import create_server, LocalModel


class FaceFixture:
    identity = 'a' * 32
    def __init__(self, root):
        self.output = root / 'fixture.mp4';self.output.write_bytes(b'transport fixture, not real video')
        self.text = None
    def health(self): return {'status':'configured-unverified','missing':[]}
    def submit(self, text): self.text = text;return self.identity
    def job(self, identity):
        if identity == self.identity: return {'state':'ready','path':str(self.output),'url':'/api/media/'+identity+'.mp4'}


class ModelFixture(BaseHTTPRequestHandler):
    requests = []
    model_ids = ['test-chat']
    result = None

    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(json.dumps({'data':[{'id':name} for name in self.model_ids]}).encode())

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.requests.append(data)
        answer = 'A test reply grounded in the supplied history.'
        self.send_response(200); self.end_headers()
        self.wfile.write(json.dumps(self.result if self.result is not None else {'choices':[{'message':{'content':answer}}]}).encode())

    def log_message(self, *args):
        pass


class MacDemoTests(unittest.TestCase):
    def setUp(self):
        ModelFixture.requests = []; ModelFixture.model_ids = ['test-chat']; ModelFixture.result = None
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        (root / 'aria-final.html').write_text('<meta name="aria-reasoning-url" content="https://example.invalid/"><body><script src="local-ai.js?v=3"></script></body>')
        (root / 'secret.py').write_text('private')
        (root / '.private.js').write_text('private')
        self.model = ThreadingHTTPServer(('127.0.0.1', 0), ModelFixture)
        self.app = create_server(root, 0, LocalModel(self.model.server_port))
        for service in [self.model, self.app]:
            threading.Thread(target=service.serve_forever, daemon=True).start()
            self.addCleanup(service.server_close); self.addCleanup(service.shutdown)
        self.url = f'http://127.0.0.1:{self.app.server_port}'

    def request(self, path, data=None, origin=None, headers=None, method=None):
        headers = {'Content-Type':'application/json', **(headers or {})}
        if origin: headers['Origin'] = origin
        req = Request(self.url + path, data=None if data is None else json.dumps(data).encode(), headers=headers, method=method)
        return urlopen(req, timeout=3)

    def test_page_uses_local_reasoning_without_cloud_fallback(self):
        with self.request('/') as response: page = response.read().decode()
        self.assertIn(self.url + '/', page)
        self.assertNotIn('example.invalid', page)
        self.assertNotIn('local-ai.js', page)
        self.assertIn('mac-demo/status.js', page)

    def test_followups_and_reference_information_reach_local_model(self):
        history = [{'role':'user', 'content':'Revenue was 90000.'}, {'role':'assistant', 'content':'What is your budget?'}]
        with self.request('/ask', {'question':'Explain that simply.', 'history':history, 'information':'Budget is 100000.'}) as response:
            self.assertIn('test reply', json.load(response)['answer'])
        messages = ModelFixture.requests[-1]['messages']
        self.assertEqual(messages[1:3], history)
        self.assertIn('Budget is 100000.', messages[-1]['content'])
        with self.request('/ask', {'question':'Different session'}) as response: response.read()
        self.assertEqual(len(ModelFixture.requests[-1]['messages']), 2)

    def test_cross_origin_and_private_files_rejected(self):
        for path in ['/secret.py', '/.private.js', '/mac-demo/']:
            with self.assertRaises(HTTPError) as error: self.request(path)
            self.assertEqual(error.exception.code, 404)
        with self.assertRaises(HTTPError) as error:
            self.request('/ask', {'question':'test'}, 'https://example.invalid')
        self.assertEqual(error.exception.code, 403)

    def test_no_local_model_is_reported_truthfully(self):
        self.app.model = LocalModel(1)
        with self.assertRaises(HTTPError) as error: self.request('/health')
        self.assertEqual(error.exception.code, 503)
        self.assertIn('LM Studio is not responding', json.loads(error.exception.read())['detail'])

    def test_facial_reply_is_paired_to_its_text_and_private_path_is_hidden(self):
        face = FaceFixture(Path(self.temp.name));self.app.face = face
        with self.request('/api/reply', {'text':'Explain profit versus cash flow.'}) as response:
            identity = json.load(response)['id']
        self.assertEqual(face.text, 'Explain profit versus cash flow.')
        with self.request('/api/job/' + identity) as response: job = json.load(response)
        self.assertNotIn('path', job)
        with self.request(job['url']) as response:
            self.assertEqual(response.headers['Content-Type'], 'video/mp4')
            self.assertEqual(response.read(), face.output.read_bytes())
        with self.assertRaises(HTTPError): self.request('/api/media/' + 'b'*32 + '.mp4')
        with self.assertRaises(HTTPError): self.request('/api/reply', {'text':'test'}, 'https://example.invalid')

    def test_multiple_models_require_explicit_selection(self):
        ModelFixture.model_ids = ['small-chat', 'large-chat']
        with self.assertRaises(HTTPError) as error: self.request('/ask', {'question':'Hello'})
        self.assertIn('Multiple chat models', json.loads(error.exception.read())['detail'])
        self.assertEqual(ModelFixture.requests, [])
        self.app.model.model = 'small-chat'
        with self.request('/ask', {'question':'Hello'}) as response: response.read()
        self.assertEqual(ModelFixture.requests[-1]['model'], 'small-chat')

    def test_malformed_model_answer_returns_recoverable_error(self):
        for result in [{'choices':[]}, {'choices':[None]}, {'choices':[{'message':None}]}]:
            ModelFixture.result = result
            with self.assertRaises(HTTPError) as error: self.request('/ask', {'question':'Hello'})
            self.assertEqual(error.exception.code, 400)
            self.assertIn('answer', json.loads(error.exception.read())['detail'])

    def test_video_range_head_and_invalid_range(self):
        face = FaceFixture(Path(self.temp.name));self.app.face = face
        url = '/api/media/' + face.identity + '.mp4'
        with self.request(url, headers={'Range':'bytes=0-3'}) as response:
            self.assertEqual(response.status, 206); self.assertEqual(response.read(), face.output.read_bytes()[:4])
            self.assertEqual(response.headers['Accept-Ranges'], 'bytes')
        with self.request(url, headers={'Range':'bytes=-4'}) as response:
            self.assertEqual(response.read(), face.output.read_bytes()[-4:])
        with self.request(url, method='HEAD') as response:
            self.assertEqual(int(response.headers['Content-Length']), face.output.stat().st_size)
            self.assertEqual(response.read(), b'')
        with self.assertRaises(HTTPError) as error: self.request(url, headers={'Range':'bytes=99999-'})
        self.assertEqual(error.exception.code, 416)


if __name__ == '__main__': unittest.main()
