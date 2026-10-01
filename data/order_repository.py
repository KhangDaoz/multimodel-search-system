import json
from pathlib import Path
class OrderRepository:
    def __init__(self):
        self.orders = json.loads((Path(__file__).parent / 'orders.json').read_text())
    def find_order(self, order_id, customer_id):
        return next((o for o in self.orders if o['order_id'].lower() == order_id.lower() and o['customer_id'] == customer_id), None)
    def latest_order(self, customer_id):
        return max((o for o in self.orders if o['customer_id'] == customer_id), key=lambda o: o['date'], default=None)
