# Assignment 06 — V02 plan and acceptance checklist

Date: 2026-10-07. Table 4 is the marking rubric in the assignment PDF.
This is a self-assessment, not a promise of the lecturer's grade.

## Plan approved by the user's V02 instruction

1. Preserve the V01 baseline and inspect the added report and native UML.
2. Install offline Vosk speech recognition and its English model. Record real
   microphone audio in the browser; decode audio in SpeechService. Provide
   permission, silence, unsupported-device and missing-model error states.
3. Replace synthetic catalog pictures with attributed product photography and
   matching titles/metadata. Add category, price and availability filters,
   useful details, ratings, a local shopping bag and responsive product cards.
4. Implement weighted text/image score fusion using the common query schema.
   Keep candidate retrieval and ranking separate; show score contributions.
5. Expand meaningful unit/HTTP/browser/audio checks, evaluate held-out image
   transformations and real audio fixtures, retain known failures.
6. Update native VP models, export diagram screenshots, synchronize the report
   with implementation, compile the PDF, and package source/demo evidence.

## Table 4: planned self-assessment before implementation

| Component | Maximum | Target | Acceptance evidence |
|---|---:|---:|---|
| Requirements analysis | 10 | 10 | Actor, FR/NFR and traceable acceptance criteria in report |
| Use Case Diagram | 15 | 14 | Native VP actor/use cases/generalizations, exported figure |
| Three-Layer Architecture | 20 | 19 | Native components/dependencies; UI → services → repositories |
| Sequence Diagram | 10 | 9 | Actual audio → transcript → query → retrieval → ranking |
| Python implementation | 20 | 19 | Runnable web/CLI, audio STT, validated filters and inputs, tests |
| Multimodal search | 10 | 9 | Text + image fusion, normalized contributions, adjustable weight |
| Experimental evaluation | 5 | 5 | Query count, successes/rate, latency, failure analysis, audio/image probes |
| Report quality | 5 | 4 | Compiled PDF, 11 recommended sections, consistent current screenshots |
| Demonstration | 5 | 5 | Saved text/real-audio/image/fusion demos and desktop/mobile screenshots |
| **Total** | **100** | **94** | Proceed because plan targets >90; reassess from actual evidence |

## Completion checks

- [x] Real audio is decoded; the web voice mode does not accept a typed simulation.
- [x] Product pictures correspond to their actual catalog entries.
- [x] Fusion and filters work through both service and HTTP interfaces.
- [x] Audio, invalid input, order ownership, filters and ranking checks pass.
- [x] Desktop/mobile browser checks pass without overflow or JS exceptions.
- [x] Native VP diagrams and report match the V02 implementation.
- [x] PDF, README, dataset/images, source and demo results are present.
- [x] Final rubric self-assessment is recorded with limitations.

## Final V02 evidence-based self-assessment

The plan was implemented. The score remains **94/100** on the assignment's
Table 4; it is separate from the query success rate (93.33%).

| Component | Score | Actual evidence / remaining deduction |
|---|---:|---|
| Requirements analysis | 10/10 | Report section 3: 11 functional and 6 non-functional requirements, acceptance evidence |
| Use Case Diagram | 14/15 | Native Customer, 7 required use cases, correct specialization; combined search documented as an additional flow |
| Three-Layer Architecture | 19/20 | Native 3 packages/15 components; dependencies corrected to actual UI orchestration and repository access; resource details remain conceptual |
| Sequence Diagram | 9/10 | Saved VP real-audio sequence with all required participants; error alternatives are tested/documented rather than separately modeled |
| Python implementation | 19/20 | Runnable web/CLI, real offline Vosk, distinct retrieval/ranking, common schema, valid filters; small local prototype |
| Multimodal search | 9/10 | Weighted normalized text/image contributions, endpoint invariants and shared filters; no learned vision/semantic encoder |
| Experimental evaluation | 5/5 | 30 fixed cases, outcomes/latency, retained failures, scope and non-comparable V01 baseline disclosed |
| Report quality | 4/5 | Locally compiled 12-page PDF, preserved Vietnamese cover, 11 sections, native figures and real running-web screenshot; VP evaluation watermark retained |
| Demonstration | 5/5 | Saved text/audio/image/fusion/order JSON and CLI text, desktop/mobile/voice/fusion screenshots |
| **Total** | **94/100** | Self-assessment only; lecturer grading may differ |

Verification: **25/25 unit/HTTP tests**, **19/19 browser checks**,
**28/30 queries**, **27/27 acceptance cases**, and submission consistency checks.
See `results/tests.txt`, `results/browser-verification.json`,
`results/evaluation.json`, `results/demo.json`, `results/vpp_verification.txt`
and `results/submission-verification.json`.

Browser recording was exercised through a Chromium virtual microphone supplied
with synthesized speech. MediaRecorder, FFmpeg and Vosk ran without STT mocks.
This confirms the integration, not a physical microphone or human accent accuracy.
The `black bag` synthetic recording fails recognition; the unstated budget probe
also fails. Both are retained. Vision checks use self-images and a transformed
query, not an independent real-world photo benchmark.

Installed locally: `.venv`, FFmpeg already on PATH, and the official English model
under `models/`. The server runs at `http://127.0.0.1:8000`.
The submission ZIP includes a reproducible model download script; environments
and the downloaded model are omitted from that compact source archive.
