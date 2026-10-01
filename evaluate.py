"""Predefined top-1 expectations; failures are retained in results, not hidden."""
import json,time
from pathlib import Path
from main import build_ui
CASES=[
 ('text','black shoes',1,'Exact two-token relevance; ID tie break'),
 ('voice','find running shoes',1,'Nike/Adidas tie resolved by ID'),
 ('text','find Nike shoes under 100 dollars',5,'Strict price filter'),
 ('text','blue shoes',4,'Color and category'),
 ('text','red bag',9,'Color and category'),
 ('text','white shirt',7,'Color and category'),
 ('text','spaceship',None,'Unknown keyword produces no result'),
 ('text','',None,'Empty query produces no result'),
 ('text','find order O001','O001','Order owner C001'),
 ('voice','where is my latest order','20261001','Latest date for C001'),
 ('text','find order O002',None,'Other customer order excluded'),
 ('image','data/images/p01.png',1,'Self-image sanity check'),
 ('image','data/images/p04.png',4,'Self-image sanity check'),
 ('image','data/images/query_blue_shoe.png',4,'Perturbed image, held out from index'),
 ('text','dark sneakers',1,'Semantic synonym expectation: baseline cannot satisfy'),
 ('text','black shoes',5,'Budget preference unstated in query: baseline ignores price ranking'),
 ('image','data/images/p05.png',5,'Identical images cannot distinguish product identities'),
]
def evaluate():
 ui=build_ui(); rows=[]
 for mode,value,expected,note in CASES:
  start=time.perf_counter();r=ui.submit(mode,value)
  actual=r['order']['order_id'] if r['order'] else (r['results'][0]['product']['id'] if r['results'] else None)
  rows.append(dict(mode=mode,input=value,expected=expected,actual=actual,success=actual==expected,note=note,latency_ms=round((time.perf_counter()-start)*1000,3)))
 successful=sum(r['success'] for r in rows)
 result=dict(total=len(rows),successful=successful,success_rate=successful/len(rows),criterion='Expected top-1 product/order ID, or no result. Cases fixed before running.',scope='Small synthetic dataset; includes self-image sanity checks, one perturbed query, and limitation probes. Not a generalization benchmark.',cases=rows)
 Path('results').mkdir(exist_ok=True);Path('results/evaluation.json').write_text(json.dumps(result,indent=2))
 lines=[f"Queries: {len(rows)} | Successful: {successful} | Success rate: {result['success_rate']:.2%}", '| Mode | Input | Expected | Actual | Success |','|---|---|---|---|---|']
 for r in rows:lines.append(f"| {r['mode']} | {r['input']} | {r['expected']} | {r['actual']} | {'Yes' if r['success'] else 'No'} |")
 Path('results/evaluation.md').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__':evaluate()
