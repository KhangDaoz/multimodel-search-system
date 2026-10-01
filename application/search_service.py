import re
class SearchService:
    def __init__(self, repository, vector_index, ranking_service, order_repository):
        self.repository, self.vector_index = repository, vector_index
        self.ranking_service, self.order_repository = ranking_service, order_repository
    def retrieve_text(self, query):
        candidates = []
        for p in self.repository.all_products():
            limit = query['filters']['max_price']
            if limit is not None and p['price'] >= limit:
                continue
            words = set(re.findall(r'[a-z0-9]+', ' '.join(str(p[k]) for k in ('name','category','color','description')).lower()))
            score = sum(t in words for t in set(query['tokens']))
            if score:
                candidates.append((p, score))
        return candidates
    def retrieve_image(self, query):
        return [(self.repository.find_product(pid),score) for pid,score in self.vector_index.retrieve(query['embedding'])]
    def search(self, query, top_k=5):
        if query['intent'] == 'order':
            if 'latest' in query['tokens']:
                order = self.order_repository.latest_order(query['customer_id'])
            else:
                match = re.search(r'order\s+([a-z0-9]+)', query['query'])
                order = self.order_repository.find_order(match.group(1), query['customer_id']) if match else None
            return {'query':query, 'processing':['normalize query','resolve order intent','check customer ownership','lookup order'], 'results':[], 'order':order}
        candidates = self.retrieve_image(query) if query['type'] == 'image' else self.retrieve_text(query)
        return {'query':query, 'processing':(['encode image','cosine retrieval'] if query['type']=='image' else ['normalize/tokenize','keyword retrieval','price filter']) + ['rank candidates','top-k'],
                'candidate_count':len(candidates),'results':self.ranking_service.rank(candidates,top_k),'order':None}
    def view_product(self, product_id):
        return self.repository.find_product(product_id)
    def view_order(self, order_id, customer_id):
        return self.order_repository.find_order(order_id, customer_id)

    def list_products(self):
        return self.repository.all_products()
    def product_image(self, product_id):
        return self.repository.image_bytes(product_id)
