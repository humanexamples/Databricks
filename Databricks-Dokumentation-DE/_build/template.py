"""Shared HTML->PDF template and renderer for the Databricks-Dokumentation-DE project.

Usage (from any authoring script):
    from template import render_pdf
    render_pdf(
        out_pdf=r"C:\...\01 .../01 Titel.pdf",
        title="Titel des Dokuments",
        subtitle="Themenordner / Kurs-Quelle",
        body_html="<h2>...</h2><p>...</p>...",   # full body content, already valid HTML
        build_name="01_ingestion_ueberblick",     # unique slug, used for temp html filename
    )

Body HTML conventions (use these CSS classes so rendering looks consistent):
    <p> ... </p>                          normal paragraph
    <h2>Section</h2> / <h3>Sub</h3>       headings
    <pre class="code sql">...</pre>       SQL code block (verbatim, HTML-escaped by caller!)
    <pre class="code python">...</pre>    Python code block
    <figure class="img"><img src="REL_OR_ABS_PATH"><figcaption>Bildunterschrift</figcaption></figure>
    <div class="docbox"><strong>Ergänzt aus der offiziellen Databricks-Dokumentation:</strong> ... <a href="URL">Quelle</a></div>
"""
import subprocess
import os

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BUILD_DIR = os.path.dirname(os.path.abspath(__file__))

CSS = """
@page { margin: 20mm 18mm 18mm 18mm; }
body { font-family: 'Segoe UI', Calibri, Arial, sans-serif; color:#1a1a1a; line-height:1.55; font-size:11.5pt; }
h1 { font-size:24pt; color:#0b3d2e; margin-bottom:2pt; }
.subtitle { color:#4a4a4a; font-size:12pt; margin-top:0; margin-bottom:18pt; border-bottom:2px solid #ff3621; padding-bottom:10pt; }
h2 { font-size:16pt; color:#0b3d2e; margin-top:22pt; border-left:5px solid #ff3621; padding-left:8pt; }
h3 { font-size:13pt; color:#1a1a1a; margin-top:16pt; }
p { margin:8pt 0; text-align:justify; }
ul, ol { margin:6pt 0; padding-left:22pt; }
li { margin:3pt 0; }
code { font-family:'Consolas','Cascadia Mono',monospace; background:#f0f0f0; padding:1pt 4pt; border-radius:3pt; font-size:10pt; }
pre.code { font-family:'Consolas','Cascadia Mono',monospace; background:#f5f5f5; border:1px solid #ddd; border-left:4px solid #1b3139; border-radius:4pt; padding:10pt 12pt; font-size:9.5pt; line-height:1.4; white-space:pre-wrap; word-wrap:break-word; margin:10pt 0; page-break-inside:avoid; }
pre.code.sql { border-left-color:#ff3621; }
pre.code.python { border-left-color:#00a972; }
figure.img { margin:14pt 0; text-align:center; page-break-inside:avoid; }
figure.img img { max-width:75%; max-height:75mm; border:1px solid #ccc; border-radius:3pt; }
figcaption { font-size:9pt; color:#666; margin-top:5pt; font-style:italic; }
.docbox { background:#eef7f2; border:1px solid #b6ddc8; border-radius:5pt; padding:10pt 14pt; margin:16pt 0; font-size:10.5pt; }
.docbox strong { color:#0b3d2e; }
table { border-collapse:collapse; width:100%; margin:10pt 0; font-size:10pt; }
th, td { border:1px solid #ccc; padding:5pt 8pt; text-align:left; }
th { background:#f0f0f0; }
.footer-note { margin-top:26pt; padding-top:8pt; border-top:1px solid #ddd; font-size:8.5pt; color:#888; }
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head>
<body>
<h1>{title}</h1>
<p class="subtitle">{subtitle}</p>
{body}
<p class="footer-note">Databricks-Dokumentation (Deutsch) &mdash; erstellt aus internem Kursmaterial, erg\u00e4nzt mit Inhalten der offiziellen Databricks-Dokumentation (docs.databricks.com).</p>
</body></html>"""


def render_pdf(out_pdf: str, title: str, subtitle: str, body_html: str, build_name: str):
    html = TEMPLATE.format(title=title, subtitle=subtitle, body=body_html, css=CSS)
    html_path = os.path.join(BUILD_DIR, build_name + ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    out_pdf_abs = os.path.abspath(out_pdf)
    os.makedirs(os.path.dirname(out_pdf_abs), exist_ok=True)
    file_url = "file:///" + os.path.abspath(html_path).replace("\\", "/")
    cmd = [EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           f'--print-to-pdf={out_pdf_abs}', file_url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if not os.path.exists(out_pdf_abs):
        raise RuntimeError(f"PDF wurde nicht erzeugt: {result.stdout}\n{result.stderr}")
    return out_pdf_abs
