import os
import math
import pandas as pd
import numpy as np
import svgwrite

print("=== GENERAZIONE GRAFICI VETTORIALI SVG CON SVGWRITE ===")

os.makedirs("reports/figures/radar", exist_ok=True)

df_proj = pd.read_parquet("data/processed/proiezioni_2031_multiscenario.parquet")
df_base = pd.read_parquet("data/processed/database_unificato.parquet")

df_nat_base = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['scenario_id'] == 'scenario_baseline')].copy()
df_base_nat = df_base[df_base['tipo_territorio'] == 'Nazionale'][['disciplina', 'classe_rischio_legale', 'notti_mese', 'ore_settimanali', 'reperibilita_mese']].copy()

df_nat_base = pd.merge(df_nat_base, df_base_nat, on='disciplina', how='left')

# ==============================================================================
# 1. FIGURA: Ranking Nazionale ISOO al 2031 (Tutte le 52 Discipline)
# ==============================================================================
print("1. Creazione reports/figures/isoo_ranking_nazionale.svg...")
df_sorted = df_nat_base.sort_values('isoo', ascending=True).reset_index(drop=True)

dwg = svgwrite.Drawing("reports/figures/isoo_ranking_nazionale.svg", size=(1150, 1650), profile='full')
dwg.add(dwg.rect((0, 0), (1150, 1650), fill="#ffffff"))

# Titoli
dwg.add(dwg.text("PROIEZIONE OCCUPAZIONALE AL 2031 PER SPECIALIZZAZIONE IN ITALIA", insert=(575, 45), text_anchor="middle", font_size="20px", font_family="Arial, sans-serif", font_weight="bold", fill="#111111"))
dwg.add(dwg.text("Indice di Saturazione e Opportunità Occupazionale (ISOO) - Coorte SSM 2026-2031 (Scenario Baseline)", insert=(575, 75), text_anchor="middle", font_size="13px", font_family="Arial, sans-serif", fill="#555555"))

margin_left = 340
plot_width = 720
bar_height = 20
bar_gap = 7
start_y = 120
max_isoo = 2.4

def isoo_to_x(val):
    return margin_left + (val / max_isoo) * plot_width

x_08 = isoo_to_x(0.80)
dwg.add(dwg.line((x_08, start_y - 15), (x_08, start_y + len(df_sorted) * (bar_height + bar_gap)), stroke="#2e7d32", stroke_width=1.5, stroke_dasharray="4,4"))
dwg.add(dwg.text("Soglia Carenza (0.80)", insert=(x_08, start_y - 20), text_anchor="middle", font_size="11px", font_family="Arial, sans-serif", font_weight="bold", fill="#2e7d32"))

x_115 = isoo_to_x(1.15)
dwg.add(dwg.line((x_115, start_y - 15), (x_115, start_y + len(df_sorted) * (bar_height + bar_gap)), stroke="#f57f17", stroke_width=1.5, stroke_dasharray="4,4"))
dwg.add(dwg.text("Soglia Equilibrio (1.15)", insert=(x_115, start_y - 20), text_anchor="middle", font_size="11px", font_family="Arial, sans-serif", font_weight="bold", fill="#f57f17"))

x_145 = isoo_to_x(1.45)
dwg.add(dwg.line((x_145, start_y - 15), (x_145, start_y + len(df_sorted) * (bar_height + bar_gap)), stroke="#c62828", stroke_width=1.5, stroke_dasharray="4,4"))
dwg.add(dwg.text("Soglia Rischio Pletora (1.45)", insert=(x_145, start_y - 20), text_anchor="middle", font_size="11px", font_family="Arial, sans-serif", font_weight="bold", fill="#c62828"))

for i, row in df_sorted.iterrows():
    y = start_y + i * (bar_height + bar_gap)
    val = row['isoo']
    b_len = (val / max_isoo) * plot_width
    
    if val < 0.80:
        color = "#2e7d32"
    elif val <= 1.15:
        color = "#43a047"
    elif val <= 1.45:
        color = "#f57f17"
    else:
        color = "#c62828"
        
    dwg.add(dwg.text(f"{row['disciplina']}", insert=(margin_left - 12, y + 15), text_anchor="end", font_size="11px", font_family="Arial, sans-serif", fill="#222222"))
    dwg.add(dwg.rect((margin_left, y), (b_len, bar_height), rx=3, ry=3, fill=color, opacity=0.9))
    dwg.add(dwg.text(f"{val:.2f}", insert=(margin_left + b_len + 8, y + 15), font_size="11px", font_family="Arial, sans-serif", font_weight="bold", fill="#333333"))

dwg.save()
print("  -> Salvata reports/figures/isoo_ranking_nazionale.svg")

# ==============================================================================
# 2. FIGURA: Matrice 4 Quadranti QoL vs REP
# ==============================================================================
print("2. Creazione reports/figures/qol_vs_rep_scatter.svg...")
dwg_q = svgwrite.Drawing("reports/figures/qol_vs_rep_scatter.svg", size=(1100, 750), profile='full')
dwg_q.add(dwg_q.rect((0, 0), (1100, 750), fill="#ffffff"))

dwg_q.add(dwg_q.text("TRADE-OFF TRA QUALITÀ DELLA VITA E REDDITIVITÀ ECONOMICA POTENZIALE", insert=(550, 40), text_anchor="middle", font_size="18px", font_family="Arial, sans-serif", font_weight="bold", fill="#111111"))
dwg_q.add(dwg_q.text("Confronto tra le 52 Discipline Medico-Chirurgiche e dei Servizi in Italia", insert=(550, 65), text_anchor="middle", font_size="12px", font_family="Arial, sans-serif", fill="#555555"))

qx_min, qx_max = 80, 1020
qy_min, qy_max = 100, 670
mid_x = (qx_min + qx_max) / 2
mid_y = (qy_min + qy_max) / 2

dwg_q.add(dwg_q.rect((mid_x, qy_min), (qx_max - mid_x, mid_y - qy_min), fill="#e8f5e9", opacity=0.6))
dwg_q.add(dwg_q.text("ALTA QoL / ALTO GUADAGNO", insert=((mid_x + qx_max)/2, qy_min + 30), text_anchor="middle", font_size="12px", font_weight="bold", fill="#2e7d32"))

dwg_q.add(dwg_q.rect((qx_min, qy_min), (mid_x - qx_min, mid_y - qy_min), fill="#ffebee", opacity=0.6))
dwg_q.add(dwg_q.text("BASSA QoL / ALTO GUADAGNO", insert=((qx_min + mid_x)/2, qy_min + 30), text_anchor="middle", font_size="12px", font_weight="bold", fill="#c62828"))

dwg_q.add(dwg_q.rect((mid_x, mid_y), (qx_max - mid_x, qy_max - mid_y), fill="#e3f2fd", opacity=0.6))
dwg_q.add(dwg_q.text("ALTA QoL / GUADAGNO SSN STANDARD", insert=((mid_x + qx_max)/2, mid_y + 30), text_anchor="middle", font_size="12px", font_weight="bold", fill="#1565c0"))

dwg_q.add(dwg_q.rect((qx_min, mid_y), (mid_x - qx_min, qy_max - mid_y), fill="#fff3e0", opacity=0.6))
dwg_q.add(dwg_q.text("BASSA QoL / GUADAGNO SSN STANDARD", insert=((qx_min + mid_x)/2, mid_y + 30), text_anchor="middle", font_size="12px", font_weight="bold", fill="#e65100"))

dwg_q.add(dwg_q.line((mid_x, qy_min), (mid_x, qy_max), stroke="#777777", stroke_width=1.5, stroke_dasharray="5,5"))
dwg_q.add(dwg_q.line((qx_min, mid_y), (qx_max, mid_y), stroke="#777777", stroke_width=1.5, stroke_dasharray="5,5"))

def scale_qol_x(q):
    return qx_min + (q / 100.0) * (qx_max - qx_min)

def scale_rep_y(r):
    r_k = r / 1000.0
    pct = (r_k - 70.0) / (150.0 - 70.0)
    return qy_max - pct * (qy_max - qy_min)

area_col = {"Medica": "#1976d2", "Chirurgica": "#d32f2f", "Servizi": "#388e3c", "Cure Primarie*": "#f57c00"}

important_labels = [
    "Dermatologia e venereologia", "Oftalmologia", "Chirurgia plastica, ricostruttiva ed estetica",
    "Cardiochirurgia", "Neurochirurgia", "Chirurgia generale", "Ortopedia e traumatologia",
    "Medicina d'emergenza-urgenza", "Medicina Generale (MMG*)", "Pediatria", "Psichiatria",
    "Anestesia Rianimazione, Terapia Intensiva e del dolore", "Malattie dell'apparato cardiovascolare",
    "Statistica sanitaria e Biometria", "Medicina del lavoro", "Radiodiagnostica"
]

for _, row in df_nat_base.iterrows():
    cx = scale_qol_x(row['qol_score_base'])
    cy = scale_rep_y(row['rep_lorda_annua'])
    c = area_col.get(row['area'], "#555555")
    
    dwg_q.add(dwg_q.circle((cx, cy), r=6.5, fill=c, stroke="#222222", stroke_width=0.8, opacity=0.85))
    
    name = row['disciplina']
    if name in important_labels:
        sname = name.replace("Malattie dell'apparato ", "").replace("Chirurgia plastica, ricostruttiva ed estetica", "Chir. Plastica").replace("Anestesia Rianimazione, Terapia Intensiva e del dolore", "Anestesia").replace("Statistica sanitaria e Biometria", "Statistica").replace("Ortopedia e traumatologia", "Ortopedia")
        dwg_q.add(dwg_q.text(sname, insert=(cx + 8, cy + 4), font_size="9.5px", font_family="Arial, sans-serif", font_weight="bold", fill="#222222"))

dwg_q.add(dwg_q.text("Qualità della Vita (QoL Score 0-100)  →  (Punteggio elevato = Meno notti, Meno reperibilità, Minore stress)", insert=(550, 715), text_anchor="middle", font_size="12px", font_weight="bold", fill="#333333"))
dwg_q.add(dwg_q.text("← Redditività Lorda Annua Stimata (da 70k€ a 150k€)", insert=(30, 385), text_anchor="middle", transform="rotate(-90 30 385)", font_size="12px", font_weight="bold", fill="#333333"))

dwg_q.save()
print("  -> Salvata reports/figures/qol_vs_rep_scatter.svg")

# ==============================================================================
# 3. FIGURA: Generazione dei 52 Radar Charts Vettoriali (SVG)
# ==============================================================================
print("3. Creazione 52 Radar Charts in reports/figures/radar/...")

def safe_filename(name):
    s = name.lower()
    for src, tgt in [("à", "a"), ("è", "e"), ("é", "e"), ("ì", "i"), ("ò", "o"), ("ù", "u")]:
        s = s.replace(src, tgt)
    return s.replace(" ", "_").replace("'", "").replace(",", "").replace("*", "").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_")

radar_labels = [
    "Opportunità SSN",
    "Potenziale Privato",
    "Qualità della Vita",
    "Serenità Medico-Legale",
    "Flessibilità Territorio"
]

for _, row in df_nat_base.iterrows():
    name = row['disciplina']
    area = row['area']
    isoo = row['isoo']
    prob_ssn = row['probabilita_bando_ssn_pct']
    qol = row['qol_score_base']
    rep_priv = row['rep_privato_stimato']
    r_legale = row['classe_rischio_legale']
    
    v_ssn = prob_ssn
    v_priv = min(100.0, (rep_priv / 70000.0) * 100.0)
    v_qol = qol
    v_leg = 100.0 - ((r_legale - 1) / 4.0 * 100.0)
    v_terr = max(20.0, min(100.0, (1.5 - isoo) * 80.0 + 30.0))
    
    vals = [v_ssn, v_priv, v_qol, v_leg, v_terr]
    
    size = 450
    center_x, center_y = size / 2, size / 2 + 15
    radius = 135
    
    dwg_r = svgwrite.Drawing(f"reports/figures/radar/{safe_filename(name)}.svg", size=(size, size), profile='full')
    dwg_r.add(dwg_r.rect((0, 0), (size, size), fill="#ffffff"))
    
    dwg_r.add(dwg_r.text(name, insert=(size/2, 26), text_anchor="middle", font_size="13px", font_weight="bold", fill="#111111", font_family="Arial, sans-serif"))
    dwg_r.add(dwg_r.text(f"Area {area} | ISOO 2031: {isoo:.2f}", insert=(size/2, 44), text_anchor="middle", font_size="11px", fill="#666666", font_family="Arial, sans-serif"))
    
    for pct in [0.25, 0.50, 0.75, 1.0]:
        pts = []
        for a_idx in range(5):
            angle = -math.pi / 2 + a_idx * (2 * math.pi / 5)
            r_cur = radius * pct
            pts.append((center_x + r_cur * math.cos(angle), center_y + r_cur * math.sin(angle)))
        dwg_r.add(dwg_r.polygon(pts, fill="none", stroke="#e0e0e0", stroke_width=1))
        
    for a_idx, label in enumerate(radar_labels):
        angle = -math.pi / 2 + a_idx * (2 * math.pi / 5)
        ax_end = (center_x + radius * math.cos(angle), center_y + radius * math.sin(angle))
        dwg_r.add(dwg_r.line((center_x, center_y), ax_end, stroke="#cccccc", stroke_width=1))
        
        lbl_r = radius + 22
        lx = center_x + lbl_r * math.cos(angle)
        ly = center_y + lbl_r * math.sin(angle)
        anchor = "middle"
        if math.cos(angle) > 0.3:
            anchor = "start"
        elif math.cos(angle) < -0.3:
            anchor = "end"
        dwg_r.add(dwg_r.text(label, insert=(lx, ly + 4), text_anchor=anchor, font_size="9.5px", font_weight="bold", fill="#444444", font_family="Arial, sans-serif"))
        
    poly_pts = []
    for a_idx, v in enumerate(vals):
        angle = -math.pi / 2 + a_idx * (2 * math.pi / 5)
        r_val = radius * (v / 100.0)
        poly_pts.append((center_x + r_val * math.cos(angle), center_y + r_val * math.sin(angle)))
        
    if isoo < 0.80:
        fcol = "#2e7d32"
    elif isoo <= 1.15:
        fcol = "#43a047"
    elif isoo <= 1.45:
        fcol = "#f57f17"
    else:
        fcol = "#c62828"
        
    dwg_r.add(dwg_r.polygon(poly_pts, fill=fcol, opacity=0.35, stroke=fcol, stroke_width=2.5))
    
    for px, py in poly_pts:
        dwg_r.add(dwg_r.circle((px, py), r=4, fill=fcol, stroke="#ffffff", stroke_width=1.5))
        
    dwg_r.save()

print("  -> Generati tutti i 52 radar chart SVG con successo.")
print("=== GENERAZIONE GRAFICA COMPLETATA ===")
