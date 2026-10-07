# FORME — Assignment 06 V02

A three-layer e-commerce search prototype with **text, real offline voice,
product-photo search and weighted text + image search**. It includes a responsive
storefront, 15 photographed sample products, common filters, product details,
customer-scoped order lookup and a browser-local shopping bag.

## Install and run

Python **3.10+** (verified here on Python 3.14), **FFmpeg on PATH**, and the packages
in `requirements.txt` are required. No API key or cloud account is needed.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/setup_voice.py
python main.py
```

On Windows activate with `.venv\Scripts\Activate.ps1` in PowerShell; use
`.venv\Scripts\activate.bat` in cmd. Install FFmpeg and ensure `ffmpeg -version`
works in that terminal. Common FFmpeg installers: `sudo apt install ffmpeg`
(Ubuntu/Debian), `sudo dnf install ffmpeg-free` (Fedora), `brew install ffmpeg`
(macOS), or `winget install Gyan.FFmpeg` (Windows).

The setup script downloads the official **vosk-model-small-en-us-0.15** English
model (~40 MB; Apache 2.0). It is already installed in this workspace under
`models/`; the script is safe to rerun. Override its path with `VOSK_MODEL_PATH`.
Dependencies/model require Internet for first installation. All search, audio
recognition, photographs, Bootstrap and UI assets then work locally offline.

Open **http://127.0.0.1:8000**. Stop with Ctrl+C. Use `python main.py --port 8080`
if port 8000 is busy. The server binds to localhost. This project has not been
published to a cloud hosting provider.

## Use the storefront

- **Text:** try `blue shoes`, `dark sneakers`, `Nike shoes under 100 dollars`,
  `black bag`, or `where is my latest order`.
- **Voice:** press **Start recording**, grant microphone access and speak in
  **English**. Press **Stop & search**; recording also stops after 12 seconds.
  The page shows what Vosk recognized and searches automatically. Alternatively
  upload a real WAV/WebM/Ogg/MP4 recording. There is no typed transcript in the
  web voice mode. Audio is processed temporarily and discarded by the server.
- **Image:** upload a photograph. Try `data/images/p03.png` or the transformed
  query `data/images/query_blue_trainers.png`. Product details offer sample-image
  download. Files must be at most 5 MB and images at most 20 megapixels.
- **Text + image:** enter keywords and upload an image. Adjust **Text importance**:
  0% uses image scores, 100% uses text scores, 50% combines both equally.
- **Filters:** choose category, minimum price, strict maximum price and in-stock
  only, then apply. Filters affect retrieval in every product-search mode.
  A textual `under`/`below` ceiling and form ceiling use the stricter value.
- **Details and bag:** cards display real catalog photos, sample ratings, price
  and stock. Open details or add available items to the shopping bag. Quantities
  cannot exceed sample stock. The bag persists in localStorage in this browser;
  it does not reserve inventory or process payments.
- **Orders:** C001 owns O001 and 20261001 (latest); C002 owns O002. Customer ID is a
  demo identity, not login/authentication. Lookup checks record ownership.

Microphone capture needs permission and a supported browser on **localhost or
HTTPS**. Chrome was checked with real MediaRecorder. Permission denial, missing
hardware, silence, invalid audio and missing model are handled. Audio upload is
available when microphone capture is unsupported. Recognition is English-only
and may mishear words; re-record a clearer query if necessary.

## Command-line demonstration

```bash
python main.py --cli
python main.py --mode text --query 'Nike shoes under 100 dollars' --top-k 3
python main.py --mode audio --query tests/fixtures/blue_shoes.wav
python main.py --mode image --query data/images/p03.png
python main.py --mode multimodal --query 'blue shoes' \
  --image data/images/p03.png --text-weight 0.7
python main.py --mode text --query 'find order O002' --customer C002
python main.py --json
```

`--mode audio` reads actual audio bytes and recognizes them. The legacy
`--mode voice --query 'blue shoes'` option remains an explicitly simulated
transcript adapter for CLI regression compatibility; the web rejects typed
voice requests. `--mode`/`--json` select CLI; `--web` and `--cli` are mutually
exclusive. Use `--help` for all flags. Image/audio paths are relative to your
terminal; catalog paths are resolved relative to the project modules.

## Architecture and method

```text
Customer → presentation (browser/HTTP handler/SearchUI)
         → application (Query/Speech/Image/Search/Ranking services)
         → data (Product/Order repositories, JSON, images, VectorIndex)
```

Text, recognized voice, images and combined inputs create the same query fields:
`type`, `intent`, `query`, `tokens`, `embedding`, `filters`, `customer_id`,
`text_weight`. UI data access goes through application services. `main.build_ui`
is the composition root. Candidate retrieval and final ranking are separate.

Text relevance is matched distinct query tokens / total distinct query tokens,
with a finite English synonym dictionary. Image descriptors normalize foreground,
fit a 16×16 RGB image and invert channels to reduce white-background influence
(768 features). This is **handcrafted pixel similarity**, not a pretrained vision
model. Cosine similarity is clamped to [0,1]. The index is built in memory at
startup. Combined relevance is:

`score = text_weight × text_score + (1 − text_weight) × image_score`

The response exposes both contributions. Filters remove ineligible candidates
before ranking. Ranking uses descending score, ascending ID for ties, then top-k.
Similarity/relevance scores are not correctness probabilities. Image retrieval
has no learned relevance-rejection threshold and can return unrelated neighbors.

HTTP routes: `GET /api/catalog` (optional category/min_price/max_price/in_stock),
`GET /api/products/<id>`, `GET /api/product-images/<id>`, `GET /api/voice-status`,
`POST /api/search` (text/image/multimodal), `POST /api/voice-search` (Base64 audio),
`GET /static/<path>`. JSON request bodies are capped at 8 MB. Uploaded recordings
are capped at 15 seconds and decoded with a timeout. Invalid data returns 400;
missing voice installation returns 503. Browser microphone capture stops at 12
seconds. Product limit is 1–15 on the web.

## Project files

```text
main.py                       Composition root, web/CLI
application/                  Query, speech, image, retrieval, fusion, ranking
presentation/                 HTTP server, SearchUI, HTML/CSS/JS and local assets
data/                         Catalog, orders, product photographs and provenance
models/                       Downloaded Vosk model (ignored by Git)
tests/                        Service/HTTP/audio tests and actual WAV fixtures
tools/setup_voice.py          Reproducible voice model installation
tools/verify_browser.py       Browser checks and current screenshots
tools/update_report.py        V02 report with tables from recorded evidence
tools/verify_submission.py    Submission/UML/report consistency checks
requirements.txt              Runtime NumPy, Pillow and Vosk
requirements-dev.txt          Optional Playwright for browser verification
evaluate.py                   Fixed V02 queries, latency, demos and failures
results/                      Tests, evaluation, demos, browser/UML evidence
uml/Assignment06.vpp          Editable native VP V02 project
uml/Assignment06_V01.vpp      Preserved V01 project
reports/Assignment06_Report.tex  Current English report source
reports/Assignment06_Report.pdf  Compiled V02 report
reports/figures/              Current VP and running-storefront screenshots
reports/archive/              Preserved original V01 LaTeX
V02_CHECKLIST.md               Plan, Table 4 rubric and final evidence
```

## Verification and results

```bash
python -m unittest discover -s tests -v
python evaluate.py
python tools/verify_submission.py
# Optional browser suite:
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tools/verify_browser.py
# Or point CHROME_PATH at an existing Chromium/Chrome executable.
```

Current evidence: **25/25 unit/HTTP tests**, **19/19 browser checks**, **28/30
queries (93.33%)**, including **27/27 acceptance cases** and three labeled
limitation probes. Evaluation writes `results/evaluation.json`, a full Markdown
table and `results/demo.json`. CLI/audio/fusion outputs are also saved as text.
The V01 baseline (14/17) is retained; dataset/cases changed, so the two rates
must not be presented as a controlled benchmark comparison.

Actual audio fixtures are synthesized with eSpeak NG. Chromium's virtual
microphone feeds such a WAV into real MediaRecorder; audio decoding/Vosk are
not mocked. The checks verify integration, **not human accent accuracy or a
physical microphone**. A `black bag` recording is misrecognized and its failure
is retained. An unstated budget preference also fails by design. A semantic
probe passes through a catalog description match without proving semantic AI.

The photo checks use catalog self-images and a resized/rotated image, not a large
independent photo dataset. Small sample data, English aliases, pixel descriptors,
recognition errors, demo identity and JSON/in-memory storage remain limitations.
Real image/semantic embeddings, human speech trials and authentication are
future extensions. The V02 rubric self-assessment is **94/100**, not a guaranteed
grading outcome. See `V02_CHECKLIST.md` for evidence and deductions.

## Report and submission

The compiled PDF and editable LaTeX are in `reports/`. The current report has the
11 recommended sections, native VP figures, actual audio-web screenshot, saved
demo scores, evaluation/failures and the Table 4 self-assessment. Rebuild source
tables with `python tools/update_report.py` after evaluation. Compile the report
with pdfLaTeX (twice) or Tectonic; see `reports/OVERLEAF_README.md`.

`uml/Assignment06.vpp` opens in Visual Paradigm 18.1+. Figures were exported from
the saved V02 project. V01 originals remain preserved. Catalog provenance:
`data/README.md`; storefront assets: `presentation/static/ASSETS.md`;
audio-fixture scope: `tests/fixtures/README.md`.

References: [Vosk installation](https://alphacephei.com/vosk/install),
[official models](https://alphacephei.com/vosk/models),
[MediaRecorder](https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder),
[DummyJSON catalog](https://github.com/Ovi/DummyJSON/blob/master/database/products.json).
