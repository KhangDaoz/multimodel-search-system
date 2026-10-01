import re
class QueryService:
    STOP = {'find','show','me','a','an','the','for','please','products','product','my','is','where','dollars','under','below'}
    def text_query(self, text, mode='text', customer_id='C001'):
        normalized = ' '.join(re.findall(r"[a-z0-9]+", text.lower()))
        price_match = re.search(r'(?:under|below)\s+\$?(\d+(?:\.\d+)?)', text.lower())
        tokens = [t for t in normalized.split() if t not in self.STOP and not t.isdigit()]
        intent = 'order' if 'order' in tokens else 'product'
        return {'type': mode, 'intent': intent, 'query': normalized, 'tokens': tokens,
                'embedding': None, 'filters': {'max_price': float(price_match.group(1)) if price_match else None},
                'customer_id': customer_id}
    def voice_query(self, text, customer_id='C001'):
        return self.text_query(text, 'voice', customer_id)
    def image_query(self, embedding, customer_id='C001'):
        return {'type':'image','intent':'product','query':'','tokens':[], 'embedding':embedding,
                'filters':{'max_price':None},'customer_id':customer_id}
