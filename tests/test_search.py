import unittest
from main import build_ui
from data.vector_index import cosine_similarity
from application.ranking_service import RankingService
class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.ui=build_ui()
    def test_modes_common_schema_and_equivalent_text_voice(self):
        a=self.ui.submit('text','black shoes');b=self.ui.submit('voice','black shoes')
        self.assertEqual(a['results'],b['results'])
        self.assertEqual(set(a['query']),set(self.ui.submit('image','data/images/p01.png')['query']))
    def test_dataset_integrity(self):
        repo=self.ui.search_service.repository
        self.assertGreaterEqual(len(repo.all_products()),10)
        for p in repo.all_products():self.assertTrue(repo.image_path(p).is_file())
    def test_price_filter(self):
        r=self.ui.submit('text','find Nike shoes under 100 dollars')
        self.assertEqual(r['results'][0]['product']['id'],5)
        self.assertTrue(all(x['product']['price']<100 for x in r['results']))
    def test_retrieval_separate_from_rank(self):
        q=self.ui.query_service.text_query('blue shoes')
        candidates=self.ui.search_service.retrieve_text(q)
        self.assertNotEqual(candidates[0][0]['id'],4)
        self.assertEqual(self.ui.search_service.ranking_service.rank(candidates)[0]['product']['id'],4)
    def test_image_self_match_and_cosine(self):
        self.assertEqual(self.ui.submit('image','data/images/p01.png')['results'][0]['product']['id'],1)
        self.assertAlmostEqual(cosine_similarity([1,0],[1,0]),1)
        self.assertEqual(cosine_similarity([0,0],[1,0]),0)
        with self.assertRaises(ValueError):cosine_similarity([1],[1,2])
    def test_order_ownership_and_latest(self):
        self.assertEqual(self.ui.submit('text','find order O001')['order']['status'],'Shipped')
        self.assertIsNone(self.ui.submit('text','find order O002')['order'])
        self.assertEqual(self.ui.submit('voice','where is my latest order')['order']['order_id'],'20261001')
    def test_empty_and_unknown_query(self):
        for q in ('','!!!','spaceship'):self.assertEqual(self.ui.submit('text',q)['results'],[])
    def test_top_k_and_invalid_inputs(self):
        self.assertEqual(len(self.ui.submit('text','shoes',top_k=2)['results']),2)
        with self.assertRaises(ValueError):RankingService().rank([],0)
        with self.assertRaises(ValueError):self.ui.submit('invalid','x')
        with self.assertRaises(OSError):self.ui.submit('image','missing.png')
if __name__=='__main__':unittest.main()
