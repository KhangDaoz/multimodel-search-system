import base64
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from main import build_ui
from presentation.web_server import make_handler

class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(build_ui()))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()
    def post(self, payload, path="/api/search"):
        request = Request(self.base+path, json.dumps(payload).encode(), {'Content-Type':'application/json'})
        try:
            with urlopen(request) as response: return response.status, json.load(response)
        except HTTPError as error:
            with error: return error.code, json.load(error)
    def test_page_and_details(self):
        with urlopen(self.base) as response: self.assertIn(b'Image search', response.read())
        with urlopen(self.base+'/api/products/1') as response: self.assertEqual(json.load(response)['id'], 1)
    def test_text_and_real_voice(self):
        status, text = self.post({'mode':'text','query':'blue shoes','top_k':3})
        self.assertEqual(status,200); self.assertEqual(text['results'][0]['product']['id'],3)
        self.assertEqual(len(text['results']),3)
        self.assertEqual(self.post({'mode':'voice','query':'blue shoes'})[0],400)
        audio = base64.b64encode(Path('tests/fixtures/blue_shoes.wav').read_bytes()).decode()
        status, voice = self.post({'audio':audio,'top_k':3},'/api/voice-search')
        self.assertEqual(status,200); self.assertEqual(voice['results'][0]['product']['id'],3)
        self.assertEqual(voice['speech']['source'],'audio')

    def test_image_upload(self):
        image=Path(__file__).resolve().parents[1]/'data/images/p03.png'
        status, response=self.post({'mode':'image','image':base64.b64encode(image.read_bytes()).decode()})
        self.assertEqual(status,200); self.assertEqual(response['results'][0]['product']['id'],3)
        self.assertIsNone(response['query']['embedding'])
    def test_order_owner(self):
        self.assertIsNone(self.post({'query':'find order O002','customer':'C001'})[1]['order'])
        self.assertEqual(self.post({'query':'find order O002','customer':'C002'})[1]['order']['order_id'],'O002')
    def test_invalid_input_and_recovery(self):
        for payload in [{'query':''},{'query':'shoes','top_k':0},{'mode':'image','image':'%%%invalid'},
                        {'mode':'image','image':base64.b64encode(b'not an image').decode()},[],
                        {'mode':'unknown','query':'shoes'}]:
            status,result=self.post(payload); self.assertEqual(status,400); self.assertIn('error',result)
        self.assertEqual(self.post({'query':'shoes'})[0],200)

    def test_catalog_product_images_and_static_assets(self):
        with urlopen(self.base+'/api/catalog') as response:
            self.assertEqual(len(json.load(response)['products']),15)
        with urlopen(self.base+'/api/product-images/1') as response:
            self.assertEqual(response.headers['Content-Type'],'image/png')
            self.assertTrue(response.read().startswith(b'\x89PNG'))
        for path in ['/static/store.css','/static/store.js','/static/vendor/bootstrap.min.css','/static/images/hero-sneaker.jpg']:
            with urlopen(self.base+path) as response: self.assertGreater(len(response.read()),100)
        for path in ['/static/../web_server.py','/static/%2e%2e/web_server.py','/api/product-images/999']:
            try:
                with urlopen(self.base+path) as response: self.fail('Expected 404')
            except HTTPError as error:
                with error: self.assertEqual(error.code,404)

    def test_fusion_filters_and_voice_status(self):
        image = base64.b64encode(Path('data/images/p03.png').read_bytes()).decode()
        status,r = self.post({'mode':'multimodal','query':'blue shoes','image':image,'text_weight':.7,'filters':{'category':'shoes','max_price':100}})
        self.assertEqual(status,200); self.assertEqual(r['results'][0]['product']['id'],3)
        self.assertIn('signals',r['results'][0])
        self.assertTrue(all(x['product']['price'] < 100 for x in r['results']))
        with urlopen(self.base+'/api/catalog?category=shirt&in_stock=true') as response:
            self.assertEqual(len(json.load(response)['products']),4)
        with urlopen(self.base+'/api/voice-status') as response:
            self.assertTrue(json.load(response)['ready'])
        self.assertEqual(self.post({'audio':'invalid'},'/api/voice-search')[0],400)
        self.assertEqual(self.post({'query':'shoes','filters':{'max_price':-1}})[0],400)

    def test_default_launches_web_and_cli_remains_available(self):
        from unittest.mock import patch
        from main import main
        with patch('sys.argv',['main.py']), patch('presentation.web_server.serve') as serve:
            main()
            serve.assert_called_once()
        with patch('sys.argv',['main.py','--cli']), patch('presentation.web_server.serve') as serve, patch('builtins.print'):
            main()
            serve.assert_not_called()
