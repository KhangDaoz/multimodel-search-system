"""Generate the V02 LaTeX body from saved evaluation/catalog evidence and the original cover."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
report = ROOT/'reports/Assignment06_Report.tex'
original = (ROOT/'reports/archive/Assignment06_Report_V01.tex').read_text()
header = original.split('\\section{Introduction}')[0]
header = header.replace('% Compiler: pdfLaTeX. No local compilation has been performed.','% V02. Compile with pdfLaTeX or Tectonic; generated evidence tables are reproducible.')
header = header.replace('\\setstretch{1.5}','\\setstretch{1.10}')
header = header.replace('[12pt,a4paper]', '[11pt,a4paper]')
header = header.replace('\\arraystretch}{1.25}', '\\arraystretch}{1.12}')
header = header.replace('\\usepackage[utf8]{inputenc}\n\\usepackage[T5]{fontenc}', r'''\usepackage{iftex}
\ifPDFTeX
\usepackage[utf8]{inputenc}
\usepackage[T5]{fontenc}
\usepackage{lmodern}
\else
\usepackage{fontspec}
\setmainfont{LiberationSerif}[Path=fonts/,Extension=.ttf,UprightFont=*-Regular,BoldFont=*-Bold,ItalicFont=*-Italic,BoldItalicFont=*-BoldItalic]
\fi''')
header = header.replace('\\usepackage{lmodern,geometry,','\\usepackage{geometry,')
header = header.replace('colorlinks=true,','colorlinks=true,hypertexnames=false,')
header = header.replace('\\textbf{\\LARGE ASSIGNMENT 06 REPORT}','\\textbf{\\LARGE ASSIGNMENT 06 REPORT -- V02}')
ps = json.loads((ROOT/'data/products.json').read_text())
evaluation = json.loads((ROOT/'results/evaluation.json').read_text())
demos = json.loads((ROOT/'results/demo.json').read_text())

def escape(value):
    s = str(value)
    for old,new in (('\\',r'\textbackslash{}'),('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#'),('$',r'\$')): s=s.replace(old,new)
    return s

def rows(items): return '\n'.join(' & '.join(escape(x) for x in row)+r' \\' for row in items)

body = r'''
\section{Introduction}
V02 extends the initial prototype into an interactive e-commerce search storefront. A customer can type keywords, speak into a microphone, upload an audio recording, select a product photograph, or combine text with an image. Every input reaches a common query representation and a shared retrieval/ranking flow. The purpose remains the relationship between requirements, native UML design and executable Python services.

The three-layer design is retained. V01 used typed voice transcripts and synthetic product shapes. V02 recognizes actual audio with an offline Vosk model, displays fifteen photographed products, applies shared category/price/availability filters and implements weighted text--image fusion. The report records test evidence and failed cases rather than claiming production-level recognition.

\section{Problem Description}
The main actor is Customer. Examples include ``blue shoes'', ``Nike shoes under 100 dollars'', a spoken product request, an uploaded photograph, and ``where is my latest order?''. Product results show photographs, names, sample prices, availability, relevance scores and optional fusion contributions. Order results show identifier, status, date, total and line items.

The catalog contains five shoes, five shirts and five bags adapted from DummyJSON. Each record stores metadata and the original photograph URL. Colors were checked against the pictures. One shirt is deliberately marked out of stock. Ratings are sample data, not verified customer reviews. Orders O001 and 20261001 belong to C001; O002 belongs to C002. Line prices and totals match the new catalog.

\begin{table}[H]\centering\footnotesize
\caption{Inputs and observable processing in V02.}
\begin{tabularx}{\textwidth}{@{}lLL@{}}\toprule
Mode & Actual input & Processing \\\midrule
Text & Keywords and optional filters & Normalize, alias matching, retrieval and ranking \\
Voice & Microphone or audio-file bytes & FFmpeg PCM conversion, Vosk recognition, text query \\
Image & Product photograph & Foreground normalization, descriptor, cosine retrieval \\
Combined & Keywords plus photograph & Text/image scores, weighted fusion, shared filters \\
\bottomrule\end{tabularx}\end{table}
The website also provides product details and a shopping bag saved in the current browser. It does not process payments or reserve stock. The customer field is a demonstration identity, not authentication. No cloud deployment is required by this assignment; this submission runs on localhost.

\newpage
\section{Requirements Analysis}
The Customer is the external actor. SpeechService and repositories are internal components. Functional requirements and acceptance evidence are explicit below.
\begin{table}[H]\centering\footnotesize
\caption{Functional requirements with traceable verification.}
\begin{tabularx}{\textwidth}{@{}lLL@{}}\toprule
ID & Requirement & Acceptance evidence \\\midrule
FR01 & At least ten products with matching pictures & Fifteen distinct photographs and complete metadata; dataset integrity test \\
FR02 & Keyword search and short price requests & Blue shoes ranks product 3; Nike under 100 ranks product 2 \\
FR03 & Real voice input on the web & WAV and MediaRecorder audio reach Vosk; typed web voice requests rejected \\
FR04 & Image similarity search & Self-images and resized/rotated product 3 query checked \\
FR05 & Common query representation & Same dictionary fields across modes; schema test \\
FR06 & Separate retrieval and top-k ranking & Unsorted candidates ranked by score, then ID \\
FR07 & Product and order viewing & Modal, ownership and latest-date tests \\
FR08 & Shared category, price and stock filters & Applied before ranking in text, image and combined search \\
FR09 & Text/image score fusion & Weight endpoints and numerical contributions verified \\
FR10 & Useful web storefront & Photos, sample ratings, detail modal and persistent local bag \\
FR11 & Invalid input and recovery & Invalid files/filters, silence, missing model, empty-state tests \\
\bottomrule\end{tabularx}\end{table}
\begin{table}[H]\centering\footnotesize
\caption{Non-functional requirements and limits.}
\begin{tabularx}{\textwidth}{@{}lLL@{}}\toprule
ID & Requirement & Verification / constraint \\\midrule
NFR01 & Maintainable layers & UI calls application services; data access stays in repositories \\
NFR02 & Reproducible results & Fixed catalog/cases, deterministic ID tie-break, saved artifacts \\
NFR03 & Local processing & Search and voice run offline after dependency/model installation \\
NFR04 & Robust inputs & 5 MB files, 8 MB JSON body, finite vectors/prices, bounded audio decoding \\
NFR05 & Responsive interface & Desktop 1440 px and mobile 390 px; no overflow or JS exceptions \\
NFR06 & Measured latency & Per-case time includes recognition; cold model load is disclosed \\
\bottomrule\end{tabularx}\end{table}
Voice is English-only. Recording requires microphone permission on localhost or HTTPS; audio upload provides an alternative when device capture is unavailable. The recording is processed temporarily and is not retained by the server.

\newpage
\section{Use Case Model}
The native Visual Paradigm project contains Customer and seven required use cases: Search Product, Search by Keyword, Search by Voice, Search by Image, Search Order, View Product and View Order. The three input-specific cases specialize Search Product. Their hollow triangular generalization arrows point toward the general case. Combined text/image search is an additional flow of Search Product using both input representations.
\begin{figure}[H]\centering
\includegraphics[width=.88\textwidth,height=.48\textheight,keepaspectratio]{figures/use-case.png}
\caption{Native use case diagram exported from the submitted VP project.}
\end{figure}
\begin{table}[H]\centering\footnotesize
\caption{Main and alternative customer flows.}
\begin{tabularx}{\textwidth}{@{}lLL@{}}\toprule
Use case & Main flow & Alternative flow \\\midrule
Keyword & Enter query, retrieve, filter and rank & Unknown terms produce no matches \\
Voice & Record/upload audio, recognize, construct query & Permission denial, silence or unreadable audio show an error \\
Image & Upload photo, encode and compare & Missing/oversized/corrupt image rejected \\
Combined & Enter keywords and photo, select weight & Invalid weight or missing modality rejected \\
Order & Find ID/latest for selected customer & Another customer's order remains hidden \\
\bottomrule\end{tabularx}\end{table}

\newpage
\section{Three-Layer Architecture}
The dependencies follow Presentation $\rightarrow$ Application / Intelligence $\rightarrow$ Data. The native model includes three packages, fifteen components and dependency connectors. The composition root in \texttt{main.py} wires services and repositories and builds the in-memory image index at startup.
\begin{figure}[H]\centering
\includegraphics[width=\textwidth,height=.45\textheight,keepaspectratio]{figures/architecture.png}
\caption{Three-layer component diagram; native VP packages and components.}
\end{figure}
\textbf{Presentation:} SearchUI, VoiceInput, ImageUpload and SearchResultView collect input and render responses. The web page and HTTP handler fulfill the same roles. Browser MediaRecorder collects audio; the browser does not load product JSON directly.

\textbf{Application:} QueryService normalizes input, resolves intent and validates filters. SpeechService converts actual audio and invokes the Vosk model. ImageService encodes photos. SearchService retrieves candidates and fuses scores. RankingService sorts and selects top-k. Recognition and retrieval use separate interfaces.

\textbf{Data:} ProductRepository and OrderRepository load JSON; VectorIndex holds image descriptors. ProductDatabase/OrderDatabase are represented by these files; ImageStorage is the image directory. The Vosk model is a pretrained local resource used by SpeechService. Temporary uploads are cleaned up after processing.

Filtering is an application responsibility. Category, lower price, strict upper price and availability predicates apply to every candidate mode before final ranking. The local bag is presentation state in localStorage; it does not mutate orders or stock.

\newpage
\section{UML Sequence Diagram}
The voice sequence was updated through the Visual Paradigm Open API and saved as a native project. It includes Customer, SearchUI, SpeechService, QueryService, SearchService, ProductRepository and RankingService. Its first messages now represent actual audio and recognized text rather than a simulated transcript.
\begin{figure}[H]\centering
\includegraphics[width=\textwidth,height=.48\textheight,keepaspectratio]{figures/voice-sequence.png}
\caption{Voice product search sequence exported from the V02 project.}
\end{figure}
The customer presses Start recording and grants microphone access. MediaRecorder emits encoded audio. Stop \& search (or the 12-second browser limit) ends capture and releases microphone tracks. The HTTP handler sends the audio bytes to SearchUI, which calls SpeechService.

SpeechService uses FFmpeg to obtain mono 16-bit PCM at 16 kHz. Vosk recognizes the waveform and returns an English transcript. QueryService constructs a voice query. SearchService obtains product records, scores eligible candidates, calls RankingService and returns ranked products with recognition metadata. The page displays the actual transcript and results.

The server permits at most fifteen seconds of uploaded speech, caps file/body sizes and sets a decoder timeout. Silence, invalid audio or absent model produces an actionable error. The sequence figure shows the successful product-search flow; these error branches are covered by service and HTTP tests. A recognized order request follows the OrderRepository branch instead.

\newpage
\section{Python Implementation}
The runtime uses Python 3.10+, NumPy, Pillow and Vosk 0.3.45. FFmpeg is an external executable. The official small English model is downloaded once with the setup script; it is not committed to Git. The supplied code was executed with Python 3.14 in the current environment.
\begin{lstlisting}
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/setup_voice.py
python main.py
# Open http://127.0.0.1:8000
python main.py --mode audio --query tests/fixtures/blue_shoes.wav
python main.py --mode multimodal --query "blue shoes" \
  --image data/images/p03.png --text-weight 0.7
python -m unittest discover -s tests -v
python evaluate.py
\end{lstlisting}
The web voice mode accepts real audio only. The old CLI \texttt{--mode voice} transcript adapter remains explicitly labeled for regression compatibility; \texttt{--mode audio} performs actual speech recognition. It is not used by the web voice route.
\begin{table}[H]\centering\footnotesize
\caption{Service endpoints and implementation responsibilities.}
\begin{tabularx}{\textwidth}{@{}p{62mm}L@{}}\toprule
Endpoint / module & Responsibility \\\midrule
GET /api/catalog & Catalog and category/price/stock filters via SearchService \\
GET /api/products/<id> & Details through ProductRepository \\
GET /api/product-images/<id> & Actual local catalog photograph \\
GET /api/voice-status & Model/decoder readiness and English-language support \\
POST /api/voice-search & Actual encoded audio to recognition and shared search \\
POST /api/search & Text, image or text/image query with validated filters \\
application/query\_service.py & Common fields: type, intent, query, tokens, embedding, filters, customer\_id, text\_weight \\
application/ranking\_service.py & Descending score; ascending ID tie-break; top-k \\
\bottomrule\end{tabularx}\end{table}
The browser offers local bag quantity controls and persistence, meaningful product details and no-results/error states. Sample ratings and shipping policies come from the dataset. Actual dataset pictures are used both on cards and by retrieval. Banner photos are illustrative. Checkout and authentication remain outside assignment scope.

\newpage
\section{Multimodal Search Method}
\textbf{Text representation.} Text is lowercased, normalized and tokenized. Request words and numerical price fragments are removed. A finite alias dictionary maps sneakers/trainers to shoes, handbags to bag and dark to black. This is rule-based normalization, not a semantic embedding model. Product words include name, brand, category, color and description.
\begin{equation}
S_t(p,q)=\frac{|T(q)\cap W(p)|}{|T(q)|},\qquad S_t\in[0,1].
\end{equation}
A text candidate needs a non-zero overlap. Normalizing by distinct query tokens gives a comparable scale for fusion. Partial matches can still appear: ``blue shoes'' may also match a blue shirt.

\textbf{Image representation.} EXIF orientation is applied and transparent pixels are composited on white. Images are bounded to 20 megapixels. A 128-pixel probe identifies non-white foreground, crops its bounds with padding, then fits it into a $16\times16$ RGB canvas. Inverted normalized RGB values suppress white-background contributions, producing a $16\times16\times3=768$ descriptor. This remains a handcrafted descriptor, not a learned visual embedding.
\begin{equation}
S_i(p,q)=\max\left(0,\frac{z_q^\mathsf{T}z_p}{\|z_q\|_2\|z_p\|_2}\right).
\end{equation}
Zero-norm vectors score zero; invalid dimensions/non-finite values are rejected. Cosine scores are clamped to $[0,1]$. Image retrieval considers the catalog and applies the same filters as text.

\textbf{Fusion.} For a combined request, the image and text representations coexist in the common query dictionary. Missing text overlap contributes zero, and the customer selects $\lambda\in[0,1]$:
\begin{equation}
S(p,q)=\lambda S_t(p,q)+(1-\lambda)S_i(p,q).
\end{equation}
At $\lambda=0$ the ranking equals image-only results; at $\lambda=1$ it equals text-only results. Tests verify both endpoints and numerical contributions. The page displays text score, image score and text weight. These scores measure relevance under the selected method; they are not correctness probabilities.

Explicit prices satisfy $p\geq\text{minimum}$ and $p<\text{maximum}$. An upper limit parsed from text is combined with a form limit using the stricter ceiling. In-stock filtering requires stock $>0$. Candidates are then sorted by relevance and ID. Image-only retrieval has no learned rejection threshold, so unrelated images can still return neighbors.

\newpage
\section{Experimental Results}
\subsection{Setup and recorded demonstrations}
The fixed V02 evaluation has @@TOTAL@@ queries: @@ACCEPTANCE@@ acceptance cases and three labeled limitation probes. The top-1 product/order ID (or no result) is compared with an expectation fixed in \texttt{evaluate.py}. Per-query timing is saved. Catalog pictures are self-image checks; the blue-trainer query is a resized/rotated copy excluded from the index. It is not an independent photograph.

Audio fixtures contain actual PCM waveforms synthesized by eSpeak NG. Recognition runs through FFmpeg and Vosk without transcript lookup or STT mocks. The browser microphone check feeds the fixture to a Chromium virtual audio device and uses real MediaRecorder. These checks establish the audio pipeline, not recognition accuracy for human speakers or accents.

\begin{table}[H]\centering\footnotesize
\caption{Saved demonstrations from results/demo.json.}
\begin{tabularx}{\textwidth}{@{}lLLr@{}}\toprule
Mode & Input & Top result & Score \\\midrule
@@DEMOROWS@@
\bottomrule\end{tabularx}\end{table}
The actual WAV transcript for ``find blue shoes'' is ``@@TRANSCRIPT@@''. Even with imperfect recognition, product 3 is ranked first. The other audio probe is misrecognized and retained as a failure.
\begin{figure}[H]\centering
\includegraphics[width=.94\textwidth,height=.40\textheight,keepaspectratio]{figures/voice-panel.png}
\caption{Running web voice mode: real uploaded audio and recognized transcript.}
\end{figure}

\newpage
\subsection{Outcomes, tests and failure analysis}
There are @@SUCCESSFUL@@ successful cases out of @@TOTAL@@, an overall rate of @@RATE@@. The acceptance subset passes @@PASSED@@/@@ACCEPTANCE@@. The three limitation probes are reported separately; they are not hidden from the overall count. V01's saved baseline was 14/17, but the catalog and test set changed, so these rates are not a controlled accuracy comparison.
\begin{center}$\mathrm{Success\ rate}=\frac{@@SUCCESSFUL@@}{@@TOTAL@@}\times100\%=@@RATE@@.$\end{center}
\begin{table}[H]\centering\footnotesize
\caption{Outcomes by input mode, including limitation probes.}
\begin{tabular}{@{}lrrr@{}}\toprule Mode & Queries & Successes & Rate \\\midrule
@@MODEROWS@@
\bottomrule\end{tabular}\end{table}
\begin{table}[H]\centering\footnotesize
\caption{Retained failed cases.}
\begin{tabularx}{\textwidth}{@{}LLrr@{}}\toprule Input & Explanation & Expected & Actual \\\midrule
@@FAILROWS@@
\bottomrule\end{tabularx}\end{table}
The incorrect audio transcript contains ``black man'' instead of ``black bag'', changing the retrieved products. The unstated budget-preference probe expects a cheaper shoe but the input contains no price preference; V02 intentionally uses explicit filters rather than inventing one. A semantic probe happens to pass through a description-word match, which does not imply general language understanding.

The 25 unit/HTTP tests pass. The 19 browser checks cover catalog filters, text/photo/fusion search, product modal, bag subtotal/persistence, audio upload, virtual microphone capture and track release, orders, empty states, desktop/mobile overflow and JavaScript exceptions. Full outputs are in \texttt{results/tests.txt} and \texttt{results/browser-verification.json}. Missing-model and silence errors are also tested. The complete query-level table and latencies are in \texttt{results/evaluation.md} and JSON.

Image processing includes file decoding; audio timing includes first model loading. Local text/order queries are sub-millisecond in this run, image queries are approximately 8--52 ms, and the two audio queries take approximately 0.7--1.3 seconds. Hardware/load/model caching affect these numbers; they are not production throughput claims.

\newpage
\section{Discussion}
V02 improves the user experience and architectural coverage. Product photographs now correspond to catalog entries instead of duplicate synthetic shapes. Real audio input is integrated into the existing service structure. Text/image fusion is executable and explainable, and all candidate modes share filtering. The native UML file and this report were updated alongside the code.

The catalog remains sample data. Keyword aliases cover only specified terms. The handcrafted visual descriptor is sensitive to viewpoint, lighting, background and cropping; a trained encoder would improve semantic retrieval. Vosk is a small English model and can misrecognize short requests, noise or accents. Physical microphone/human-speaker trials remain necessary. The browser handles permission denial and unavailable devices, while upload offers another real-audio path.

The local bag does not reserve inventory, and the demo identity field does not authenticate customers. JSON files and a small in-memory index meet the assignment scale, but a production system would need persistent storage, authentication, audited access control and operational monitoring. No public hosting or production commerce is claimed.

\begin{table}[H]\centering\footnotesize
\caption{Evidence-based self-assessment against assignment Table 4.}
\begin{tabularx}{\textwidth}{@{}Lrr@{}}\toprule Component & Maximum & Self-assessed \\\midrule
Requirements analysis & 10 & 10 \\
Use Case Diagram & 15 & 14 \\
Three-Layer Architecture & 20 & 19 \\
Sequence Diagram & 10 & 9 \\
Python implementation & 20 & 19 \\
Multimodal search & 10 & 9 \\
Experimental evaluation & 5 & 5 \\
Report quality & 5 & 4 \\
Demonstration & 5 & 5 \\\midrule
Total & 100 & 94 \\\bottomrule\end{tabularx}\end{table}
The score is a reasoned estimate, not a grading guarantee. Deductions reflect diagram/error-branch detail, a small dataset, handcrafted image features, recognition errors and limited human trials. The checklist links each criterion to reviewable implementation and artifacts.

\section{Conclusion}
The completed V02 demonstrates requirements analysis, native Visual Paradigm UML and a working three-layer Python storefront. Text, real voice audio, images and combined queries reach common services, retrieval and ranking. The submission includes source, catalog pictures, the editable VP model, this PDF, README, saved demonstrations and measured evaluation results. Failed cases and verification limits remain visible.

\textbf{References.} Assignment 06 specification supplied by the lecturer; Vosk installation and model documentation: \url{https://alphacephei.com/vosk/install}, \url{https://alphacephei.com/vosk/models}; MediaRecorder documentation: \url{https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder}; DummyJSON product source: \url{https://github.com/Ovi/DummyJSON}; Bootstrap documentation: \url{https://getbootstrap.com/docs/5.3/}. Source code: \url{https://github.com/KhangDaoz/multimodel-search-system}. The local V02 artifacts are the authoritative evidence for this report; no remote repository update is claimed.
\end{document}
'''
mode_rows=[]
for mode in ('text','image','multimodal','audio'):
    cases=[c for c in evaluation['cases'] if c['mode']==mode];ok=sum(c['success'] for c in cases)
    mode_rows.append((mode,len(cases),ok,f'{ok/len(cases):.2%}'))
demo_rows=[]
for demo in demos[:4]:
    result=demo['results'][0]
    value=demo['input']['input']
    if demo['input']['mode']=='audio': value='blue_shoes.wav (actual audio)'
    if demo['input']['mode']=='multimodal':value='blue shoes + p03.png, weight 0.7'
    demo_rows.append((demo['input']['mode'],value,result['product']['name'],f"{result['score']:.4f}"))
substitutions={'TOTAL':str(evaluation['total']),'ACCEPTANCE':str(evaluation['acceptance_total']),
    'SUCCESSFUL':str(evaluation['successful']),'PASSED':str(evaluation['acceptance_successful']),
    'RATE':escape(f"{evaluation['success_rate']:.2%}"),'DEMOROWS':rows(demo_rows),
    'MODEROWS':rows(mode_rows),'FAILROWS':rows((Path(c['input']).name if c['mode']=='audio' else c['input'],c['note'],c['expected'],c['actual']) for c in evaluation['cases'] if not c['success']),
    'TRANSCRIPT':escape(demos[1]['speech']['text'])}
for key,value in substitutions.items(): body=body.replace('@@'+key+'@@',value)
report.write_text(header+body)
print('Wrote V02 LaTeX with evidence-derived outcomes and demo tables')
