import json
from pathlib import Path
class ProductRepository:
    def __init__(self, path=None):
        self.base = Path(path).parent if path else Path(__file__).parent
        self.products = json.loads((Path(path) if path else self.base / 'products.json').read_text())
    def all_products(self):
        return list(self.products)
    def find_product(self, product_id):
        return next((p for p in self.products if p['id'] == product_id), None)
    def image_path(self, product):
        return self.base / product['image']

    def image_bytes(self, product_id):
        product = self.find_product(product_id)
        return self.image_path(product).read_bytes() if product else None
