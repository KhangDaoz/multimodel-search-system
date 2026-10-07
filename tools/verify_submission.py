"""Read-only checks of native UML, report, dataset and saved V02 evidence."""
import json
from pathlib import Path
import re
import sqlite3
import subprocess

ROOT = Path(__file__).resolve().parents[1]
checks = []
def check(name, condition):
    if not condition: raise AssertionError(name)
    checks.append(name)

for path in ('README.md','requirements.txt','main.py','data/products.json','data/orders.json',
             'uml/Assignment06.vpp','reports/Assignment06_Report.tex','reports/Assignment06_Report.pdf',
             'results/demo.json','results/evaluation.json','results/browser-verification.json','results/tests.txt'):
    check('Required artifact: '+path,(ROOT/path).is_file() and (ROOT/path).stat().st_size > 0)
ps = json.loads((ROOT/'data/products.json').read_text())
check('Catalog has at least 10 products',len(ps) >= 10)
for p in ps: check('Photo exists for product '+str(p['id']),(ROOT/'data'/p['image']).is_file())
for order in json.loads((ROOT/'data/orders.json').read_text()):
    check('Order total '+order['order_id'],abs(order['total']-sum(x['price']*x['quantity'] for x in order['items'])) < .001)
conn = sqlite3.connect(f'file:{ROOT}/uml/Assignment06.vpp?mode=ro',uri=True)
check('VP SQLite integrity',conn.execute('pragma integrity_check').fetchone()[0]=='ok')
diagrams = list(conn.execute('select DIAGRAM_TYPE,NAME from DIAGRAM'))
check('Three native required diagrams',{'UseCaseDiagram','ComponentDiagram','InteractionDiagram'} <= {d[0] for d in diagrams})
models = list(conn.execute('select ID,MODEL_TYPE,NAME,PARENT_ID,CAST(DEFINITION as TEXT) from MODEL_ELEMENT'))
lookup = {m[0]:m for m in models}
for use in ('Search Product','Search by Keyword','Search by Voice','Search by Image','Search Order','View Product','View Order'):
    check('Native use case '+use,any(m[1]=='UseCase' and m[2]==use for m in models))
check('Native Customer actor',any(m[1]=='Actor' and m[2]=='Customer' for m in models))
for layer in ('Presentation Layer','Application / Intelligence Layer','Data Layer'):
    check('Native package '+layer,any(m[1]=='Package' and m[2]==layer for m in models))
messages = [m[2] for m in models if m[1]=='Message']
check('Sequence represents real audio','transcribe_audio(bytes)' in messages and 'text (Vosk offline)' in messages)
check('No simulated message in V02',not any('simulated' in (name or '').lower() for name in messages))
for participant in ('Customer','SearchUI','SpeechService','QueryService','SearchService','ProductRepository','RankingService'):
    check('Native sequence participant '+participant,any(m[1] in ('InteractionLifeLine','InteractionActor') and m[2]==participant for m in models))
for m in models:
    if m[1] != 'Dependency': continue
    endpoints = {}
    for field in ('fromModel','toModel'):
        match = re.search(field+r'=<([^>]+)>',m[4])
        if match: endpoints[field] = lookup.get(match.group(1).split(':')[-1])
    if len(endpoints)==2 and all(endpoints.values()):
        source,target = endpoints['fromModel'],endpoints['toModel']
        sp,tp = lookup.get(source[3]),lookup.get(target[3])
        check('No presentation/data shortcut: '+str(source[2])+' → '+str(target[2]),not(sp and tp and sp[2]=='Presentation Layer' and tp[2]=='Data Layer'))
dependency_edges = set()
for m in models:
    if m[1] == 'Dependency':
        ids = [re.search(field+r'=<([^>]+)>',m[4]).group(1).split(':')[-1] for field in ('fromModel','toModel')]
        dependency_edges.add(tuple(lookup[identifier][2] for identifier in ids))
check('Architecture matches actual UI orchestration',all(('SearchUI',service) in dependency_edges for service in ('QueryService','SpeechService','ImageService','SearchService')))
check('Architecture retrieval/ranking dependencies',all(('SearchService',component) in dependency_edges for component in ('ProductRepository','OrderRepository','VectorIndex','RankingService')))
tex = (ROOT/'reports/Assignment06_Report.tex').read_text()
sections = re.findall(r'\\section\{([^}]+)\}',tex)
check('Eleven report sections',len(sections)==11)
check('Report labels actual recognition','offline Vosk' in tex and 'handcrafted descriptor' in tex)
check('Report has no unresolved generated placeholders','@@' not in tex)
for figure in re.findall(r'\{(figures/[^}]+)\}',tex): check('Report figure '+figure,(ROOT/'reports'/figure).is_file())
evaluation = json.loads((ROOT/'results/evaluation.json').read_text())
check('Evaluation count consistency',evaluation['total']==len(evaluation['cases']))
check('Evaluation retains failures',any(not c['success'] for c in evaluation['cases']))
check('Evaluation rate computed from actual outcomes',abs(evaluation['success_rate']-sum(c['success'] for c in evaluation['cases'])/evaluation['total']) < 1e-10)
check('Audio demo includes actual recognition',any(d.get('speech',{}).get('source')=='audio' for d in json.loads((ROOT/'results/demo.json').read_text())))
browser = json.loads((ROOT/'results/browser-verification.json').read_text())
check('Browser verified without JS exceptions',browser['passed']>=19 and not browser['javascript_errors'])
check('Test output reports success','Ran 25 tests' in (ROOT/'results/tests.txt').read_text() and (ROOT/'results/tests.txt').read_text().rstrip().endswith('OK'))
pdf_text = subprocess.run(['pdftotext',str(ROOT/'reports/Assignment06_Report.pdf'),'-'],capture_output=True,text=True,check=True).stdout
check('Compiled PDF is V02 and reports actual rate','V02' in pdf_text and '93.33%' in pdf_text and '94' in pdf_text)
check('Vietnamese cover names preserved','ĐÀO VĂN KHANG' in pdf_text and 'TRẦN ĐÌNH QUẾ' in pdf_text)
info = subprocess.run(['pdfinfo',str(ROOT/'reports/Assignment06_Report.pdf')],capture_output=True,text=True,check=True).stdout
check('Report approximately 10–12 pages',10 <= int(re.search(r'Pages:\s+(\d+)',info).group(1)) <= 12)
result = {'passed':len(checks),'checks':checks,'native_diagrams':diagrams,'report_sections':sections}
(ROOT/'results/submission-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
