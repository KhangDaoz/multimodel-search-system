import re
from application.query_service import QueryService


class SearchService:
    def __init__(self, repository, vector_index, ranking_service, order_repository):
        self.repository, self.vector_index = repository, vector_index
        self.ranking_service, self.order_repository = ranking_service, order_repository

    def _eligible(self, product, filters):
        return ((not filters['category'] or product['category'] == filters['category'])
                and (filters['min_price'] is None or product['price'] >= filters['min_price'])
                and (filters['max_price'] is None or product['price'] < filters['max_price'])
                and (not filters['in_stock'] or product['stock'] > 0))

    def retrieve_text(self, query):
        candidates = []
        tokens = set(query['tokens'])
        for product in self.repository.all_products():
            if not self._eligible(product, query['filters']):
                continue
            words = set(QueryService.tokenize(' '.join(str(product.get(k, ''))
                        for k in ('name', 'brand', 'category', 'color', 'description'))))
            score = len(tokens & words) / len(tokens) if tokens else 0.0
            if score > 0:
                candidates.append((product, score))
        return candidates

    def retrieve_image(self, query):
        return [(product, max(0.0, min(1.0, score)))
                for pid, score in self.vector_index.retrieve(query['embedding'])
                if (product := self.repository.find_product(pid)) and self._eligible(product, query['filters'])]

    def retrieve_multimodal(self, query):
        text = {p['id']: score for p, score in self.retrieve_text(query)}
        weight = query['text_weight']
        return [(p, weight * text.get(p['id'], 0.0) + (1 - weight) * image_score)
                for p, image_score in self.retrieve_image(query)
                if weight < 1 or p['id'] in text]

    def search(self, query, top_k=5):
        if type(top_k) is not int or top_k < 1:
            raise ValueError('top_k must be a positive integer')
        if query['intent'] == 'order':
            if 'latest' in query['tokens']:
                order = self.order_repository.latest_order(query['customer_id'])
            else:
                match = re.search(r'order\s+([a-z0-9]+)', query['query'])
                order = self.order_repository.find_order(match.group(1), query['customer_id']) if match else None
            return {'query': query, 'processing': ['normalize query', 'resolve order intent', 'check customer ownership', 'lookup order'], 'results': [], 'order': order}
        mode = query['type']
        if mode == 'multimodal':
            candidates = self.retrieve_multimodal(query)
            processing = ['normalize/tokenize', 'encode image', 'text and cosine retrieval', 'weighted score fusion']
        elif mode == 'image':
            candidates = self.retrieve_image(query)
            processing = ['encode image', 'cosine retrieval']
        else:
            candidates = self.retrieve_text(query)
            processing = ['normalize/tokenize', 'keyword retrieval']
        results = self.ranking_service.rank(candidates, top_k)
        if mode == 'multimodal':
            ts = {p['id']: s for p, s in self.retrieve_text(query)}
            ims = {p['id']: s for p, s in self.retrieve_image(query)}
            for result in results:
                pid = result['product']['id']
                result['signals'] = {'text': round(ts.get(pid, 0), 6), 'image': round(ims[pid], 6), 'text_weight': query['text_weight']}
        return {'query': query, 'processing': processing + ['category/price/stock filters', 'rank candidates', 'top-k'],
                'candidate_count': len(candidates), 'results': results, 'order': None}

    def view_product(self, product_id):
        return self.repository.find_product(product_id)

    def view_order(self, order_id, customer_id):
        return self.order_repository.find_order(order_id, customer_id)

    def list_products(self, filters=None):
        validated = QueryService.validate_filters(filters)
        return [p for p in self.repository.all_products() if self._eligible(p, validated)]

    def product_image(self, product_id):
        return self.repository.image_bytes(product_id)
