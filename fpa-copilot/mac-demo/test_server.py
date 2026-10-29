from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from server import create_server, LocalModel


class ModelFixture(BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        self.send_response(200); self.end_headers()
        self.wfile.write(b'{"data":[{"id":"test-chat"}]}')

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.requests.append(data)
        answer = 'A test reply grounded in the supplied history.'
        self.send_response(200); self.end_headers()
        self.wfile.write(json.dumps({'choices':[{'message':{'content':answer}}]}).encode())

    def log_message(self, *args):
        pass


class MacDemoTests(unittest.TestCase):
    def setUp(self):
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

    def request(self, path, data=None, origin=None):
        headers = {'Content-Type':'application/json'}
        if origin: headers['Origin'] = origin
        req = Request(self.url + path, data=None if data is None else json.dumps(data).encode(), headers=headers)
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


if __name__ == '__main__': unittest.main()
