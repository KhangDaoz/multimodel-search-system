"""Fixed V02 acceptance cases and explicit limitation probes; all outcomes are retained."""
import json
import time
from pathlib import Path
from main import build_ui

CASES = [
    dict(mode='text',input='black shoes',expected=1,note='Color/category relevance'),
    dict(mode='text',input='blue shoes',expected=3,note='Color/category relevance'),
    dict(mode='text',input='Nike shoes under 100 dollars',expected=2,note='Explicit budget'),
    dict(mode='text',input='Puma trainers',expected=3,note='Brand and synonym'),
    dict(mode='text',input='black bag',expected=15,note='Matching bag photograph'),
    dict(mode='text',input='blue bag',expected=11,note='Color/category'),
    dict(mode='text',input='white shirt',expected=7,note='Sold-out item remains visible without filter'),
    dict(mode='text',input='plaid shirt',expected=8,note='Product-specific keywords'),
    dict(mode='text',input='dark sneakers',expected=1,note='Finite synonym dictionary'),
    dict(mode='text',input='spaceship',expected=None,note='Unknown query'),
    dict(mode='text',input='',expected=None,note='Empty service query'),
    dict(mode='text',input='find order O001',expected='O001',note='Order owner C001'),
    dict(mode='text',input='where is my latest order',expected='20261001',note='Latest date'),
    dict(mode='text',input='find order O002',expected=None,note='Other customer excluded'),
    dict(mode='text',input='find order O002',customer='C002',expected='O002',note='Correct owner'),
    dict(mode='text',input='shoes',filters={'max_price':79.99},expected=None,note='Strict ceiling excludes boundary'),
    dict(mode='text',input='bag',filters={'category':'bag','max_price':60},expected=11,note='Category and price'),
    dict(mode='text',input='shirt',filters={'category':'shirt','in_stock':True},expected=6,note='Availability'),
    dict(mode='image',input='data/images/p01.png',expected=1,note='Self-image sanity check'),
    dict(mode='image',input='data/images/p03.png',expected=3,note='Self-image sanity check'),
    dict(mode='image',input='data/images/p05.png',expected=5,note='Distinct photograph fixes V01 duplicate'),
    dict(mode='image',input='data/images/p11.png',expected=11,note='Bag self-image'),
    dict(mode='image',input='data/images/query_blue_trainers.png',expected=3,note='Resized and rotated query, not indexed'),
    dict(mode='multimodal',input='blue shoes',image_path='data/images/p03.png',text_weight=.7,expected=3,note='Weighted text/image agreement'),
    dict(mode='multimodal',input='black bag',image_path='data/images/p15.png',text_weight=.5,expected=15,note='Combined bag query'),
    dict(mode='multimodal',input='shoes',image_path='data/images/p03.png',filters={'category':'shoes','max_price':100},expected=3,note='Fusion with filters'),
    dict(mode='audio',input='tests/fixtures/blue_shoes.wav',expected=3,note='Actual WAV decoding; eSpeak synthetic speech fixture'),
    dict(mode='audio',input='tests/fixtures/black_bag.wav',expected=15,note='Recognition robustness probe: synthetic speech',probe=True),
    dict(mode='text',input='comfortable footwear',expected=3,note='Unsupported semantic intent',probe=True),
    dict(mode='text',input='black shoes',expected=2,note='Unstated budget preference; not a functional requirement',probe=True),
]


def run_case(ui, case):
    kwargs = {k:case[k] for k in ('filters','image_path','text_weight') if k in case}
    customer = case.get('customer','C001')
    if case['mode'] == 'audio':
        return ui.submit_audio(Path(case['input']).read_bytes(),customer,filters=case.get('filters'))
    return ui.submit(case['mode'],case['input'],customer,**kwargs)


def evaluate():
    ui = build_ui(); rows = []
    for case in CASES:
        start = time.perf_counter()
        response = run_case(ui,case)
        actual = response['order']['order_id'] if response['order'] else response['results'][0]['product']['id'] if response['results'] else None
        row = dict(case,actual=actual,success=actual == case['expected'],latency_ms=round((time.perf_counter()-start)*1000,3))
        if 'speech' in response: row['recognized_text'] = response['speech']['text']
        rows.append(row)
    successful = sum(r['success'] for r in rows)
    functional = [r for r in rows if not r.get('probe')]
    result = dict(version='V02',total=len(rows),successful=successful,success_rate=successful/len(rows),
                  acceptance_total=len(functional),acceptance_successful=sum(r['success'] for r in functional),
                  criterion='Expected top-1 product/order ID or no result; cases fixed before running.',
                  scope='Small sample catalog. Self-images and one transformed query, not independent real-world visual benchmark. Audio fixtures are synthesized speech, not human microphone recordings. Limitation probes are included and labeled.',cases=rows)
    Path('results').mkdir(exist_ok=True)
    Path('results/evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
    lines = [f"Queries: {len(rows)} | Successful: {successful} | Success rate: {result['success_rate']:.2%}",
             f"Acceptance cases: {result['acceptance_successful']}/{len(functional)}; limitation probes: {len(rows)-len(functional)}.",
             '| Mode | Input | Expected | Actual | Success | Latency (ms) |','|---|---|---|---|---|---|']
    for r in rows: lines.append(f"| {r['mode']} | {r['input']} | {r['expected']} | {r['actual']} | {'Yes' if r['success'] else 'No'} | {r['latency_ms']} |")
    Path('results/evaluation.md').write_text('\n'.join(lines)+'\n'); print('\n'.join(lines))
    demos = []
    for case in (CASES[0],CASES[26],CASES[22],CASES[23],CASES[11]):
        response = run_case(ui,case); response['input'] = case
        if response['query'].get('embedding') is not None:
            response['query']['embedding_dimension'] = len(response['query']['embedding']); response['query']['embedding'] = None
        demos.append(response)
    Path('results/demo.json').write_text(json.dumps(demos,indent=2)+'\n')
    return result

if __name__ == '__main__': evaluate()
