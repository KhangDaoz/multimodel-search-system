"""Package reviewable V02 source/report/data/evidence, excluding environments and caches."""
from pathlib import Path
import zipfile
ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'dist'
TARGET.mkdir(exist_ok=True)
paths = ['README.md','V02_CHECKLIST.md','requirements.txt','requirements-dev.txt',
         'main.py','evaluate.py','application','presentation','data','tests','tools','uml','reports','results']
with zipfile.ZipFile(TARGET/'Assignment06_V02.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for part in paths:
        path = ROOT/part
        files = [path] if path.is_file() else path.rglob('*')
        for file in files:
            if not file.is_file() or '__pycache__' in file.parts or file.suffix in ('.pyc','.aux','.out','.toc','.log','.fls','.fdb_latexmk','.class'): continue
            if 'archive' in file.parts or file.name == 'Assignment06_V01.vpp' or '.vpp.bak_' in file.name or file.suffix == '.lck': continue
            archive.write(file,Path('Assignment06_V02')/file.relative_to(ROOT))
    archive.writestr('Assignment06_V02/models/README.md',
        'Download the official English model with python tools/setup_voice.py after installing requirements.\n'
        'The model is installed in the original workspace but omitted from this source submission to keep it compact.\n')
with zipfile.ZipFile(TARGET/'Assignment06_Report_Overleaf_V02.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for path in (ROOT/'reports').rglob('*'):
        if path.is_file() and ('figures' in path.parts or 'fonts' in path.parts or path.name in ('Assignment06_Report.tex','bia.png','OVERLEAF_README.md')):
            archive.write(path,path.relative_to(ROOT/'reports'))
print(TARGET/'Assignment06_V02.zip')
print(TARGET/'Assignment06_Report_Overleaf_V02.zip')
