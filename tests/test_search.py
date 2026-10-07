import math
from pathlib import Path
import unittest
from main import build_ui
from application.query_service import QueryService
from data.vector_index import cosine_similarity


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.ui = build_ui()

    def test_modes_common_schema_and_equivalent_transcript_adapter(self):
        a = self.ui.submit('text','black shoes'); b = self.ui.submit('voice','black shoes')
        self.assertEqual(a['results'],b['results'])
        for mode in ('image','multimodal'):
            result = self.ui.submit(mode,'blue shoes' if mode == 'multimodal' else 'data/images/p03.png',image_path='data/images/p03.png')
            self.assertEqual(set(a['query']),set(result['query']))

    def test_dataset_integrity_and_distinct_photographs(self):
        repo = self.ui.search_service.repository
        self.assertGreaterEqual(len(repo.all_products()),10)
        image_bytes = []
        for p in repo.all_products():
            self.assertTrue(repo.image_path(p).is_file())
            self.assertTrue(p['image_source'].startswith('https://cdn.dummyjson.com/'))
            image_bytes.append(repo.image_bytes(p['id']))
        self.assertEqual(len(image_bytes),len(set(image_bytes)))

    def test_price_filter_strict_boundary_and_decimal_tokens(self):
        response = self.ui.submit('text','find Nike shoes under 100 dollars')
        self.assertEqual(response['results'][0]['product']['id'],2)
        self.assertTrue(all(x['product']['price'] < 100 for x in response['results']))
        response = self.ui.submit('text','Nike under 79.99 dollars')
        self.assertFalse(any(x['product']['id'] == 2 for x in response['results']))
        self.assertNotIn('99',response['query']['tokens'])

    def test_filters_apply_across_all_modes(self):
        filters = {'category':'shoes','min_price':80,'max_price':120,'in_stock':True}
        for mode in ('text','image','multimodal'):
            value = 'shoes' if mode != 'image' else 'data/images/p03.png'
            r = self.ui.submit(mode,value,filters=filters,image_path='data/images/p03.png',top_k=15)
            self.assertTrue(r['results'])
            for item in r['results']:
                p = item['product']; self.assertEqual(p['category'],'shoes')
                self.assertTrue(80 <= p['price'] < 120 and p['stock'] > 0)

    def test_catalog_filter_and_sold_out_exclusion(self):
        products = self.ui.search_service.list_products({'category':'shirt','in_stock':True})
        self.assertEqual(len(products),4)
        self.assertNotIn(7,[p['id'] for p in products])

    def test_invalid_filters(self):
        for f in ([], {'max_price':math.nan},{'min_price':math.inf},{'min_price':-1},
                  {'max_price':True},{'category':'unknown'},{'in_stock':'true'},
                  {'min_price':100,'max_price':90},{'unexpected':1}):
            with self.subTest(f=f), self.assertRaises(ValueError): QueryService.validate_filters(f)

    def test_retrieval_separate_from_rank(self):
        query = self.ui.query_service.text_query('blue shoes')
        candidates = self.ui.search_service.retrieve_text(query)
        self.assertNotEqual(candidates[0][0]['id'],3)
        self.assertEqual(self.ui.search_service.ranking_service.rank(candidates)[0]['product']['id'],3)

    def test_self_images_and_held_out_transform(self):
        for pid in (1,3,5,11,15):
            with self.subTest(pid=pid): self.assertEqual(self.ui.submit('image',f'data/images/p{pid:02}.png')['results'][0]['product']['id'],pid)
        self.assertEqual(self.ui.submit('image','data/images/query_blue_trainers.png')['results'][0]['product']['id'],3)

    def test_cosine_validation(self):
        self.assertAlmostEqual(cosine_similarity([1,0],[1,0]),1)
        self.assertEqual(cosine_similarity([0,0],[1,0]),0)
        for a,b in (([1],[1,2]),([math.nan],[1]),([[1]],[1])):
            with self.assertRaises(ValueError): cosine_similarity(a,b)

    def test_fusion_endpoints_and_contributions(self):
        for weight,mode in ((0,'image'),(1,'text')):
            r = self.ui.submit('multimodal','blue shoes',image_path='data/images/p01.png',text_weight=weight,top_k=15)
            expected = self.ui.submit(mode,'data/images/p01.png' if mode == 'image' else 'blue shoes',top_k=15)
            self.assertEqual([(x['product']['id'],x['score']) for x in r['results']],[(x['product']['id'],x['score']) for x in expected['results']])
        r = self.ui.submit('multimodal','blue shoes',image_path='data/images/p03.png',text_weight=.7)
        self.assertEqual(r['results'][0]['product']['id'],3)
        for x in r['results']:
            s = x['signals']; self.assertAlmostEqual(x['score'],.7*s['text']+.3*s['image'],places=5)

    def test_invalid_fusion_weight_and_order_intent(self):
        for weight in (-.1,1.1,True,math.nan,'0.5'):
            with self.assertRaises(ValueError): self.ui.submit('multimodal','blue shoes',image_path='data/images/p03.png',text_weight=weight)
        for q in ('','find order O001'):
            with self.assertRaises(ValueError): self.ui.submit('multimodal',q,image_path='data/images/p03.png')

    def test_order_ownership_and_latest(self):
        self.assertEqual(self.ui.submit('text','find order O001')['order']['status'],'Shipped')
        self.assertIsNone(self.ui.submit('text','find order O002')['order'])
        self.assertEqual(self.ui.submit('voice','where is my latest order')['order']['order_id'],'20261001')

    def test_alias_and_empty_unknown_query(self):
        self.assertEqual(self.ui.submit('text','dark sneakers')['results'],self.ui.submit('text','black shoes')['results'])
        for q in ('','!!!','spaceship'): self.assertEqual(self.ui.submit('text',q)['results'],[])

    def test_top_k_and_invalid_inputs(self):
        self.assertEqual(len(self.ui.submit('text','shoes',top_k=2)['results']),2)
        for k in (0,True,1.5):
            with self.assertRaises(ValueError): self.ui.submit('text','shoes',top_k=k)
        with self.assertRaises(ValueError): self.ui.submit('invalid','x')
        with self.assertRaises(OSError): self.ui.submit('image','missing.png')

if __name__ == '__main__': unittest.main()
