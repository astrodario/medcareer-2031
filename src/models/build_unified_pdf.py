# -*- coding: utf-8 -*-
"""
build_unified_pdf.py
Unifica il Report Nazionale e le 52 Schede Monografiche in un unico documento PDF
ad altissima definizione con grafica vettoriale, tabelle formattate e styling tipografico professionale.
"""

import os
import re
import base64
import subprocess
import mistune

print("=== INIZIO COMPILAZIONE VOLUME UNIFICATO PDF ===")

base_dir = os.path.abspath(".")
reports_dir = os.path.join(base_dir, "reports")
figures_dir = os.path.join(reports_dir, "figures")
spec_dir = os.path.join(reports_dir, "specializzazioni")

output_html = os.path.join(reports_dir, "MEDCAREER_2031_GUIDA_COMPLETA.html")
output_pdf = os.path.join(reports_dir, "MEDCAREER_2031_GUIDA_COMPLETA.pdf")

# Funzione per codificare file SVG in Base64 Data URI
def svg_to_base64_data_uri(svg_path):
    if os.path.exists(svg_path):
        with open(svg_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/svg+xml;base64,{b64}"
    return ""

# Parser markdown con estensioni tabelle
markdown_parser = mistune.create_markdown(plugins=['table'])

# 1. Caricamento Report Nazionale
print("1. Caricamento e parsing del Report Nazionale...")
nat_report_path = os.path.join(reports_dir, "REPORT_NAZIONALE_MEDCAREER2031.md")
with open(nat_report_path, "r", encoding="utf-8") as f:
    nat_md = f.read()

# Pulizia link interni nel report nazionale
nat_md = nat_md.replace("specializzazioni/", "#spec-")

# Sostituzione immagini vettoriali con Base64 Data URI
isoo_svg = os.path.join(figures_dir, "isoo_ranking_nazionale.svg")
qol_svg = os.path.join(figures_dir, "qol_vs_rep_scatter.svg")

isoo_b64 = svg_to_base64_data_uri(isoo_svg)
qol_b64 = svg_to_base64_data_uri(qol_svg)

nat_md = re.sub(r"!\[Ranking Nazionale ISOO\]\(figures/isoo_ranking_nazionale\.svg\)", f'<div class="img-container"><img src="{isoo_b64}" style="max-width:100%; height:auto;" /></div>', nat_md)
nat_md = re.sub(r"!\[Trade-off QoL vs REP\]\(figures/qol_vs_rep_scatter\.svg\)", f'<div class="img-container"><img src="{qol_b64}" style="max-width:100%; height:auto;" /></div>', nat_md)

# Conversione callout GitHub
def format_callouts(text):
    text = re.sub(r">\s*\[!NOTE\]\s*\n((?:>.*\n?)*)", r'<div class="callout callout-note">\1</div>', text)
    text = re.sub(r">\s*\[!TIP\]\s*\n((?:>.*\n?)*)", r'<div class="callout callout-tip">\1</div>', text)
    text = re.sub(r">\s*\[!WARNING\]\s*\n((?:>.*\n?)*)", r'<div class="callout callout-warning">\1</div>', text)
    text = re.sub(r">\s*\[!IMPORTANT\]\s*\n((?:>.*\n?)*)", r'<div class="callout callout-important">\1</div>', text)
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    return text

nat_md = format_callouts(nat_md)
nat_html = markdown_parser(nat_md)

# 2. Caricamento di tutte le 52 Monografie
print("2. Caricamento e formattazione delle 52 schede monografiche...")
spec_files = sorted([f for f in os.listdir(spec_dir) if f.endswith(".md")])

monographs_html_list = []
for sf in spec_files:
    spec_slug = sf.replace(".md", "")
    full_path = os.path.join(spec_dir, sf)
    with open(full_path, "r", encoding="utf-8") as f:
        s_md = f.read()
    
    # Rimuovi i breadcrumbs
    s_md = re.sub(r"\[← Torna al Report Nazionale\].*", "", s_md)
    s_md = format_callouts(s_md)
    
    # Radar chart embedded
    radar_path = os.path.join(figures_dir, "radar", f"{spec_slug}.svg")
    radar_b64 = svg_to_base64_data_uri(radar_path)
    s_md = re.sub(r"!\[Radar Chart:.*?\]\(\.\./figures/radar/.*?\.svg\)", f'<div class="radar-container"><img src="{radar_b64}" style="width:340px; height:340px;" /></div>', s_md)
    
    s_html = markdown_parser(s_md)
    # Aggiungi un id per i link e un salto pagina forzato
    wrapped_html = f'<div id="spec-{spec_slug}" class="monograph-chapter">\n{s_html}\n</div>'
    monographs_html_list.append(wrapped_html)

all_monographs_html = "\n\n".join(monographs_html_list)

# 3. Assemblaggio del Documento Completo con CSS per la Stampa
print("3. Generazione layout HTML per la stampa tipografica...")

css_styles = """
<style>
@page {
    size: A4 portrait;
    margin: 1.8cm 1.6cm 1.8cm 1.6cm;
    @bottom-center {
        content: counter(page);
        font-family: Arial, sans-serif;
        font-size: 9pt;
        color: #666666;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.45;
    color: #222222;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
}

/* Copertina */
.cover-page {
    page-break-after: always;
    text-align: center;
    padding-top: 100px;
    padding-bottom: 50px;
}

.cover-title {
    font-size: 28pt;
    font-weight: 800;
    color: #0d47a1;
    margin-bottom: 15px;
    line-height: 1.2;
}

.cover-subtitle {
    font-size: 15pt;
    color: #37474f;
    margin-bottom: 40px;
    line-height: 1.4;
}

.cover-meta {
    font-size: 11pt;
    color: #616161;
    margin-top: 80px;
    border-top: 2px solid #e0e0e0;
    padding-top: 25px;
    line-height: 1.6;
}

/* Titoli e gerarchia */
h1 {
    font-size: 19pt;
    color: #0d47a1;
    border-bottom: 2px solid #1976d2;
    padding-bottom: 6px;
    margin-top: 25px;
    margin-bottom: 15px;
    page-break-after: avoid;
}

h2 {
    font-size: 14pt;
    color: #1565c0;
    margin-top: 22px;
    margin-bottom: 10px;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 4px;
    page-break-after: avoid;
}

h3 {
    font-size: 11.5pt;
    color: #2e7d32;
    margin-top: 16px;
    margin-bottom: 6px;
    page-break-after: avoid;
}

/* Tabelle */
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 10px;
    margin-bottom: 18px;
    font-size: 8.5pt;
    page-break-inside: auto;
}

tr {
    page-break-inside: avoid;
    page-break-after: auto;
}

th {
    background-color: #f0f4f8;
    color: #1a237e;
    font-weight: bold;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #dcdfe6;
}

td {
    padding: 5px 8px;
    border: 1px solid #e4e7ed;
}

tr:nth-child(even) {
    background-color: #fafbfc;
}

/* Callout Blocks */
.callout {
    padding: 10px 14px;
    margin: 14px 0;
    border-radius: 4px;
    font-size: 9pt;
    page-break-inside: avoid;
}

.callout-note {
    background-color: #e3f2fd;
    border-left: 4px solid #1976d2;
    color: #0d47a1;
}

.callout-tip {
    background-color: #e8f5e9;
    border-left: 4px solid #388e3c;
    color: #1b5e20;
}

.callout-warning {
    background-color: #fff3e0;
    border-left: 4px solid #f57c00;
    color: #e65100;
}

.callout-important {
    background-color: #f3e5f5;
    border-left: 4px solid #8e24aa;
    color: #4a148c;
}

/* Immagini */
.img-container {
    text-align: center;
    margin: 20px 0;
    page-break-inside: avoid;
}

.radar-container {
    text-align: center;
    margin: 12px 0;
    page-break-inside: avoid;
}

/* Separatori di capitolo e schede */
.monograph-chapter {
    page-break-before: always;
}

hr {
    border: 0;
    height: 1px;
    background: #e0e0e0;
    margin: 20px 0;
}

ul, ol {
    margin-top: 5px;
    margin-bottom: 12px;
    padding-left: 20px;
}

li {
    margin-bottom: 4px;
}

a {
    color: #1565c0;
    text-decoration: none;
}
</style>
"""

full_html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>MedCareer 2031 — Trattato Completo e Schede di Specializzazione</title>
{css_styles}
</head>
<body>

<!-- COPERTINA -->
<div class="cover-page">
    <div style="font-size: 14pt; font-weight: bold; color: #1976d2; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 20px;">
        Osservatorio Sanitario Nazionale — Coorte SSM 2026–2031
    </div>
    <div class="cover-title">
        MEDCAREER 2031
    </div>
    <div class="cover-subtitle">
        Modello Previsionale Scientifico sulle Opportunità Lavorative,<br>
        Fabbisogni del SSN, Qualità della Vita e Redditività Economica<br>
        per i Medici Specializzandi in Italia
    </div>
    
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; text-align: left; font-size: 9.5pt; color: #475569;">
        <strong>Volume Integrale di Orientamento Professionale:</strong><br>
        • <strong>Parte I:</strong> Rapporto Nazionale di Sintesi, Metodologia Stock-Flow, Curve Attuariali MEF, Ponderazione Demografica ISTAT e Confronto dei 3 Scenari.<br>
        • <strong>Parte II:</strong> 52 Schede Monografiche Dettagliate (51 Scuole di Specializzazione SSM + Medicina Generale MMG*) con tabelle regionali delle 21 Regioni/P.A., Scorecard QoL/REP e Radar Charts pentagonali.
    </div>

    <div class="cover-meta">
        <strong>Data di Rilascio:</strong> Novembre 2026<br>
        <strong>Destinatari:</strong> Medici Neolaureati, Candidati al Concorso SSM e Dirigenti Sanitari<br>
        <strong>Fonti Ufficiali:</strong> Ministero dell'Economia e delle Finanze (MEF), Ministero dell'Università e della Ricerca (MUR), ISTAT, ANAAO Assomed, ALS
    </div>
</div>

<!-- VOLUME I: REPORT NAZIONALE -->
<div class="national-report">
{nat_html}
</div>

<!-- SEPARATORE VOLUME II -->
<div style="page-break-before: always; text-align: center; padding-top: 150px;">
    <h1 style="font-size: 26pt; border-bottom: none; color: #0d47a1;">PARTE II</h1>
    <h2 style="font-size: 18pt; border-bottom: none; color: #37474f;">LE 52 SCHEDE MONOGRAFICHE DETTAGLIATE</h2>
    <p style="font-size: 11pt; color: #616161; max-width: 500px; margin: 20px auto;">
        Dossier specialistici analitici per ciascuna delle 52 discipline: andamento storico, multi-scenario al 2031, fabbisogno per singola Regione, scorecard e consigli strategici di carriera.
    </p>
</div>

<!-- VOLUME II: 52 MONOGRAFIE -->
{all_monographs_html}

</body>
</html>
"""

print(f"Scrittura file HTML completo ({len(full_html):,} caratteri) in {output_html}...")
with open(output_html, "w", encoding="utf-8") as f:
    f.write(full_html)

# 4. Esecuzione di Microsoft Edge Headless per la Generazione del PDF
print("4. Rendering tipografico in PDF con motore Chromium (Microsoft Edge headless)...")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

cmd = [
    edge_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={output_pdf}",
    f"file:///{output_html}"
]

res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(output_pdf):
    pdf_size = os.path.getsize(output_pdf) / (1024 * 1024)
    print(f"=== COMPILAZIONE PDF COMPLETATA CON SUCCESSO! ===")
    print(f"File PDF generato: {output_pdf}")
    print(f"Dimensione PDF: {pdf_size:.2f} MB")
else:
    print("Errore durante la generazione del PDF con Edge:", res.stderr)
