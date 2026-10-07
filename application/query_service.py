import math
import re


class QueryService:
    STOP = {'find', 'show', 'me', 'a', 'an', 'the', 'for', 'please', 'products',
            'product', 'my', 'is', 'where', 'dollars', 'under', 'below', 'with', 'and', 'of'}
    ALIASES = {'sneaker': 'shoes', 'sneakers': 'shoes', 'shoe': 'shoes',
               'trainers': 'shoes', 'trainer': 'shoes', 'shirts': 'shirt',
               'tshirt': 'shirt', 'bags': 'bag', 'handbag': 'bag',
               'handbags': 'bag', 'backpack': 'bag', 'dark': 'black'}

    @classmethod
    def tokenize(cls, text):
        return [cls.ALIASES.get(t, t) for t in re.findall(r'[a-z0-9]+', text.lower())
                if t not in cls.STOP and not t.isdigit()]

    def text_query(self, text, mode='text', customer_id='C001', filters=None):
        if not isinstance(text, str) or len(text) > 1000:
            raise ValueError('Query must be a string of at most 1000 characters')
        normalized = ' '.join(re.findall(r'[a-z0-9]+', text.lower()))
        price_match = re.search(r'(?:under|below)\s+\$?(\d+(?:\.\d+)?)', text.lower())
        tokens = self.tokenize(re.sub(r'(?:under|below)\s+\$?\d+(?:\.\d+)?', '', text.lower()))
        selected = self.validate_filters(filters)
        if price_match:
            ceiling = float(price_match.group(1))
            selected['max_price'] = min(ceiling, selected['max_price']) if selected['max_price'] is not None else ceiling
        return {'type': mode, 'intent': 'order' if 'order' in tokens else 'product',
                'query': normalized, 'tokens': tokens, 'embedding': None,
                'filters': selected, 'customer_id': customer_id, 'text_weight': 1.0}

    def voice_query(self, text, customer_id='C001', filters=None):
        return self.text_query(text, 'voice', customer_id, filters)

    def image_query(self, embedding, customer_id='C001', filters=None):
        query = self.text_query('', 'image', customer_id, filters)
        query.update(embedding=embedding, text_weight=0.0)
        return query

    def multimodal_query(self, text, embedding, customer_id='C001', filters=None, text_weight=0.5):
        if isinstance(text_weight, bool) or not isinstance(text_weight, (int, float)) or not math.isfinite(text_weight) or not 0 <= text_weight <= 1:
            raise ValueError('Text weight must be a number from 0 to 1')
        query = self.text_query(text, 'multimodal', customer_id, filters)
        if not query['tokens'] or query['intent'] != 'product':
            raise ValueError('Combined search needs product keywords and an image')
        query.update(embedding=embedding, text_weight=float(text_weight))
        return query

    @staticmethod
    def validate_filters(filters):
        if filters is not None and not isinstance(filters, dict):
            raise ValueError('Filters must be an object')
        filters = filters or {}
        if set(filters) - {'category', 'min_price', 'max_price', 'in_stock'}:
            raise ValueError('Unsupported filter')
        result = {'category': filters.get('category') or None,
                  'min_price': filters.get('min_price'), 'max_price': filters.get('max_price'),
                  'in_stock': filters.get('in_stock', False)}
        if result['category'] not in (None, 'shoes', 'shirt', 'bag'):
            raise ValueError('Unsupported category')
        if type(result['in_stock']) is not bool:
            raise ValueError('Availability filter must be boolean')
        for field in ('min_price', 'max_price'):
            value = result[field]
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0):
                raise ValueError('Prices must be finite non-negative numbers')
        if result['min_price'] is not None and result['max_price'] is not None and result['min_price'] >= result['max_price']:
            raise ValueError('Minimum price must be below the maximum price')
        return result
