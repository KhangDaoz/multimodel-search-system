# Current report: Overleaf LaTeX source

Upload `Assignment06_Report_Overleaf.zip` as a new Overleaf project, or upload
`Assignment06_Report.tex` together with the entire `figures/` directory.
Choose `Assignment06_Report.tex` as the main document and pdfLaTeX as compiler.
No local compilation has been performed.

The English cover uses the supplied information: Đào Văn Khang, B23DCVT218,
class E23TTNT01, group 04, and lecturer Assoc. Prof. Dr. Trần Đình Quế.
The institution and faculty are translated into English; proper names retain
Vietnamese diacritics. These fields can be edited at the start of the source.

Formatting follows the supplied sample: Latin Modern, 12pt A4, 1.5 line spacing,
2cm top/bottom margins, 2.2cm left/right margins, no paragraph indent, 0.35em
paragraph spacing, and 1.25 table row spacing. English captions and headings
are retained. The cover optionally loads `bia.png` from the project root;
if you have this logo, upload it beside the main .tex file. All eleven sections
and their body content remain unchanged by this formatting update.

The report has a cover, table of contents, and exactly these eleven main sections:
1. Introduction
2. Problem Description
3. Requirements Analysis
4. Use Case Model
5. Three-Layer Architecture
6. UML Sequence Diagram
7. Python Implementation
8. Multimodal Search Method
9. Experimental Results
10. Discussion
11. Conclusion

Within the eleven fixed sections, related content is grouped into a small number
of subsections. Introduction, Use Case Model, UML Sequence Diagram, and Conclusion
use continuous prose without numbered subsections. Main sections no longer force
a new page; figures remain associated with their sections.

The report explains the current default web application, the three input modes,
UML diagrams, recorded demonstrations, evaluation outcomes, and limitations.
References appear within the concluding section. Readability takes priority over
a fixed page count; there is no 10–12-page cap. The final page count will be known
when you compile on Overleaf.

`Assignment06_Report.pdf`, `report_source.md`, and `build_report.py` are historical
artifacts from the earlier report. They do not represent this rewritten LaTeX
version. The ReportLab builder does not build the current LaTeX report.
