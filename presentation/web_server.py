"""Local browser interface; persistence remains behind application services."""
import base64
import binascii
import json
import mimetypes
from urllib.parse import urlsplit, unquote
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_BODY = 8 * 1024 * 1024


def make_handler(ui):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, body, content_type='application/json'):
            if content_type == 'application/json':
                body = json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path.startswith('/static/'):
                base = Path(__file__).with_name('static').resolve()
                asset = (base / path.removeprefix('/static/')).resolve()
                if asset.is_relative_to(base) and asset.is_file():
                    self.reply(200, asset.read_bytes(), mimetypes.guess_type(asset.name)[0] or 'application/octet-stream')
                else:
                    self.reply(404, {'error': 'Asset not found'})
            elif path == '/api/catalog':
                self.reply(200, {'products': ui.search_service.list_products()})
            elif path.startswith('/api/product-images/'):
                try:
                    image = ui.search_service.product_image(int(path.rsplit('/', 1)[1]))
                    if image:
                        self.reply(200, image, 'image/png')
                    else:
                        self.reply(404, {'error': 'Image not found'})
                except (ValueError, OSError):
                    self.reply(404, {'error': 'Image not found'})
            elif path == '/':
                self.reply(200, Path(__file__).with_name('web_ui.html').read_bytes(), 'text/html; charset=utf-8')
            elif self.path.startswith('/api/products/'):
                try:
                    product = ui.search_service.view_product(int(self.path.rsplit('/', 1)[1]))
                    self.reply(200 if product else 404, product or {'error': 'Product not found'})
                except ValueError:
                    self.reply(400, {'error': 'Invalid product ID'})
            else:
                self.reply(404, {'error': 'Not found'})

        def do_POST(self):
            if self.path != '/api/search':
                self.reply(404, {'error': 'Not found'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= MAX_BODY:
                    self.reply(413, {'error': 'Request must be smaller than 8 MB'})
                    return
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError('Expected a JSON object')
                mode = payload.get('mode', 'text')
                value = payload.get('query', '')
                customer = payload.get('customer', 'C001')
                top_k = payload.get('top_k', 5)
                if type(top_k) is not int or not 1 <= top_k <= 12:
                    raise ValueError('Result limit must be an integer from 1 to 12')
                if not isinstance(customer, str) or not customer.strip():
                    raise ValueError('Customer ID is required')
                if mode == 'image':
                    encoded = payload.get('image', '')
                    if not isinstance(encoded, str) or not encoded:
                        raise ValueError('Please select an image')
                    image_bytes = base64.b64decode(encoded, validate=True)
                    with tempfile.TemporaryDirectory(prefix='assignment06-image-') as folder:
                        image_path = Path(folder) / 'query-image'
                        image_path.write_bytes(image_bytes)
                        response = ui.submit(mode, str(image_path), customer.strip(), top_k)
                    # Pixel vectors are internal data; the browser only needs scores.
                    response['query']['embedding'] = None
                else:
                    if not isinstance(value, str) or not value.strip():
                        raise ValueError('Please enter a query')
                    response = ui.submit(mode, value, customer.strip(), top_k)
                self.reply(200, response)
            except (ValueError, OSError, binascii.Error) as error:
                self.reply(400, {'error': str(error)})
    return Handler


def serve(ui, port=8000):
    server = ThreadingHTTPServer(('127.0.0.1', port), make_handler(ui))
    print(f'Open http://127.0.0.1:{server.server_port} in your browser', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
