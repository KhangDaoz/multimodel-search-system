"""Local storefront: UI → application services → repositories."""
import base64
import binascii
import json
import mimetypes
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit
from application.speech_service import SpeechUnavailable

MAX_BODY = 8 * 1024 * 1024


def make_handler(ui):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body, content_type='application/json'):
            if content_type == 'application/json':
                body = json.dumps(body, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urlsplit(self.path)
            path = unquote(url.path)
            if path.startswith('/static/'):
                base = Path(__file__).with_name('static').resolve()
                asset = (base / path.removeprefix('/static/')).resolve()
                if asset.is_relative_to(base) and asset.is_file():
                    self.reply(200, asset.read_bytes(), mimetypes.guess_type(asset.name)[0] or 'application/octet-stream')
                else:
                    self.reply(404, {'error': 'Asset not found'})
            elif path == '/api/voice-status':
                self.reply(200, ui.speech_service.status())
            elif path == '/api/catalog':
                try:
                    params = parse_qs(url.query)
                    filters = {}
                    if 'category' in params: filters['category'] = params['category'][0]
                    for field in ('min_price', 'max_price'):
                        if field in params: filters[field] = float(params[field][0])
                    if 'in_stock' in params:
                        if params['in_stock'][0] not in ('true', 'false'): raise ValueError('Invalid availability filter')
                        filters['in_stock'] = params['in_stock'][0] == 'true'
                    self.reply(200, {'products': ui.search_service.list_products(filters)})
                except ValueError as error:
                    self.reply(400, {'error': str(error)})
            elif path.startswith('/api/product-images/'):
                try:
                    image = ui.search_service.product_image(int(path.rsplit('/', 1)[1]))
                    self.reply(200, image, 'image/png') if image else self.reply(404, {'error': 'Image not found'})
                except (ValueError, OSError):
                    self.reply(404, {'error': 'Image not found'})
            elif path == '/':
                self.reply(200, Path(__file__).with_name('web_ui.html').read_bytes(), 'text/html; charset=utf-8')
            elif path.startswith('/api/products/'):
                try:
                    product = ui.search_service.view_product(int(path.rsplit('/', 1)[1]))
                    self.reply(200 if product else 404, product or {'error': 'Product not found'})
                except ValueError:
                    self.reply(400, {'error': 'Invalid product ID'})
            else:
                self.reply(404, {'error': 'Not found'})

        @staticmethod
        def decode(payload, field):
            encoded = payload.get(field, '')
            if not isinstance(encoded, str) or not encoded:
                raise ValueError(f'Please provide {field}')
            decoded = base64.b64decode(encoded, validate=True)
            if not decoded or len(decoded) > 5 * 1024 * 1024:
                raise ValueError(f'{field.capitalize()} must be smaller than 5 MB')
            return decoded

        def do_POST(self):
            if self.path not in ('/api/search', '/api/voice-search'):
                self.reply(404, {'error': 'Not found'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= MAX_BODY:
                    self.reply(413, {'error': 'Request must be smaller than 8 MB'})
                    return
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict): raise ValueError('Expected a JSON object')
                value = payload.get('query', '')
                customer = payload.get('customer', 'C001')
                top_k = payload.get('top_k', 5)
                if type(top_k) is not int or not 1 <= top_k <= len(ui.search_service.list_products()):
                    raise ValueError('Result limit must be an integer within the catalog size')
                if not isinstance(customer, str) or not customer.strip(): raise ValueError('Customer ID is required')
                filters = ui.query_service.validate_filters(payload.get('filters'))
                if self.path == '/api/voice-search':
                    response = ui.submit_audio(self.decode(payload, 'audio'), customer.strip(), top_k, filters)
                else:
                    mode = payload.get('mode', 'text')
                    if mode == 'voice':
                        raise ValueError('Voice search requires a recording sent to /api/voice-search')
                    if mode in ('image', 'multimodal'):
                        image_bytes = self.decode(payload, 'image')
                        with tempfile.TemporaryDirectory(prefix='forme-image-') as folder:
                            image_path = Path(folder) / 'query-image'
                            image_path.write_bytes(image_bytes)
                            response = ui.submit(mode, str(image_path) if mode == 'image' else value,
                                customer.strip(), top_k, filters, str(image_path), payload.get('text_weight', 0.5))
                        response['query']['embedding'] = None
                    else:
                        if mode != 'text': raise ValueError('Supported web modes: text, image, multimodal, or audio voice')
                        if not isinstance(value, str) or not value.strip(): raise ValueError('Please enter a query')
                        response = ui.submit(mode, value, customer.strip(), top_k, filters)
                self.reply(200, response)
            except SpeechUnavailable as error:
                self.reply(503, {'error': str(error)})
            except (ValueError, OSError, binascii.Error) as error:
                self.reply(400, {'error': str(error)})
    return Handler


def serve(ui, port=8000):
    server = ThreadingHTTPServer(('127.0.0.1', port), make_handler(ui))
    print(f'Open http://127.0.0.1:{server.server_port} in your browser', flush=True)
    print('Voice: ' + ui.speech_service.status()['message'], flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
