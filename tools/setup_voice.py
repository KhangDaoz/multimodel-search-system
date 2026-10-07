"""Download the official Apache-2.0 Vosk English model once, then run offline."""
from pathlib import Path
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = 'vosk-model-small-en-us-0.15'
URL = f'https://alphacephei.com/vosk/models/{NAME}.zip'

if __name__ == '__main__':
    target = ROOT / 'models'
    if (target / NAME / 'am/final.mdl').is_file():
        print('Voice model already installed')
    else:
        target.mkdir(exist_ok=True)
        print(f'Downloading {URL} (about 40 MB)')
        with tempfile.TemporaryDirectory() as folder:
            archive = Path(folder) / 'model.zip'
            urllib.request.urlretrieve(URL, archive)
            with zipfile.ZipFile(archive) as zipped:
                for name in zipped.namelist():
                    if not (target / name).resolve().is_relative_to(target.resolve()):
                        raise ValueError('Invalid archive path')
                zipped.extractall(target)
        print('Installed. FFmpeg must also be available on PATH.')
