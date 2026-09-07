import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set clean aesthetic style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

os.makedirs("reports/figures/radar", exist_ok=True)

# 1. Carica proiezioni e baseline
df_proj = pd.read_parquet("data/processed/proiezioni_2031_multiscenario.parquet")
df_nat_base = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['scenario_id'] == 'scenario_baseline')].copy()

# ==============================================================================
# FIGURA 1: Ranking Nazionale ISOO al 2031 (Tutte le 52 Discipline)
# ==============================================================================
print("Generazione Figura 1: Ranking Nazionale ISOO al 2031...")
df_sorted = df_nat_base.sort_values('isoo', ascending=True).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(12, 16), dpi=200)

colors = []
for val in df_sorted['isoo']:
    if val < 0.80:
        colors.append('#2e7d32') # Verde scuro - carenza
    elif val <= 1.15:
        colors.append('#43a047') # Verde chiaro - equilibrio
    elif val <= 1.45:
        colors.append('#f57f17') # Giallo/Arancio - competitivo
    else:
        colors.append('#c62828') # Rosso - pletora

bars = ax.barh(range(len(df_sorted)), df_sorted['isoo'], color=colors, height=0.75, alpha=0.9)

# Aggiungi soglie verticali di riferimento
ax.axvline(0.80, color='#2e7d32', linestyle='--', linewidth=1.2, alpha=0.7, label='Soglia Carenza (ISOO < 0.80)')
ax.axvline(1.15, color='#f57f17', linestyle='--', linewidth=1.2, alpha=0.7, label='Soglia Equilibrio (ISOO = 1.15)')
ax.axvline(1.45, color='#c62828', linestyle='--', linewidth=1.2, alpha=0.7, label='Soglia Rischio Pletora (ISOO > 1.45)')

ax.set_yticks(range(len(df_sorted)))
ax.set_yticklabels(df_sorted['disciplina'], fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('Indice di Saturazione e Opportunità Occupazionale (ISOO 2031)\n[Nuovi Diplomati / Fabbisogno Stimato Totale SSN + Privato]', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('PROIEZIONE OCCUPAZIONALE AL 2031 PER SPECIALIZZAZIONE IN ITALIA\nCoorte SSM 2026-2031 - Scenario Baseline', fontsize=13, fontweight='bold', pad=15)

# Aggiungi etichette numeriche
for i, (bar, val) in enumerate(zip(bars, df_sorted['isoo'])):
    ax.text(val + 0.03, i, f"{val:.2f}", va='center', fontsize=8, color='#333333', fontweight='bold')

ax.set_xlim(0, 2.4)
ax.grid(axis='x', linestyle=':', alpha=0.6)
ax.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cccccc', fontsize=9)

plt.tight_layout()
fig.savefig("reports/figures/isoo_ranking_nazionale.png", dpi=200)
plt.close(fig)
print("  -> Salvata reports/figures/isoo_ranking_nazionale.png")

# ==============================================================================
# FIGURA 2: Matrice 4 Quadranti: Qualità della Vita (QoL) vs Redditività (REP)
# ==============================================================================
print("Generazione Figura 2: Matrice QoL vs REP...")
fig, ax = plt.subplots(figsize=(13, 9), dpi=200)

x = df_nat_base['qol_score_base']
y = df_nat_base['rep_lorda_annua'] / 1000.0 # in k€

med_x = x.median()
med_y = y.median()

ax.axvline(med_x, color='#999999', linestyle='--', linewidth=1, alpha=0.7)
ax.axhline(med_y, color='#999999', linestyle='--', linewidth=1, alpha=0.7)

# Colore punti in base all'area
color_map = {
    "Medica": "#1976d2",
    "Chirurgica": "#d32f2f",
    "Servizi": "#388e3c",
    "Cure Primarie*": "#f57c00"
}
point_colors = [color_map.get(a, "#555555") for a in df_nat_base['area']]

scatter = ax.scatter(x, y, c=point_colors, s=110, alpha=0.85, edgecolors='black', linewidth=0.6)

# Annotazioni testuali selettive
labeled_specialties = [
    "Dermatologia e venereologia", "Oftalmologia", "Chirurgia plastica, ricostruttiva ed estetica",
    "Cardiochirurgia", "Neurochirurgia", "Chirurgia generale", "Ortopedia e traumatologia",
    "Medicina d'emergenza-urgenza", "Medicina Generale (MMG*)", "Pediatria", "Psichiatria",
    "Anestesia Rianimazione, Terapia Intensiva e del dolore", "Malattie dell'apparato cardiovascolare",
    "Statistica sanitaria e Biometria", "Medicina del lavoro", "Radiodiagnostica", "Medicina interna"
]

for _, r in df_nat_base.iterrows():
    name = r['disciplina']
    if name in labeled_specialties:
        short_name = name.replace("Malattie dell'apparato ", "").replace("Chirurgia plastica, ricostruttiva ed estetica", "Chir. Plastica").replace("Anestesia Rianimazione, Terapia Intensiva e del dolore", "Anestesia & Rianim.").replace("Statistica sanitaria e Biometria", "Statistica Sanitaria")
        ax.annotate(short_name, (r['qol_score_base'] + 0.8, r['rep_lorda_annua']/1000.0 + 0.4), fontsize=8, alpha=0.9, fontweight='semibold')

# Etichette quadranti
ax.text(82, 142, "ALTA QoL / ALTO GUADAGNO\n(Dermatologia, Oculistica)", fontsize=10, fontweight='bold', color='#1b5e20', ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#e8f5e9', alpha=0.8, edgecolor='#a5d6a7'))
ax.text(25, 142, "BASSA QoL / ALTO GUADAGNO\n(Chirurgie complesse, Ortopedia)", fontsize=10, fontweight='bold', color='#b71c1c', ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffebee', alpha=0.8, edgecolor='#ef9a9a'))
ax.text(82, 85, "ALTA QoL / GUADAGNO SSN\n(Servizi, Med. Lavoro, Statistica)", fontsize=10, fontweight='bold', color='#0d47a1', ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#e3f2fd', alpha=0.8, edgecolor='#90caf9'))
ax.text(25, 88, "BASSA QoL / GUADAGNO SSN\n(Emergenza Urgenza, Reparti acuti)", fontsize=10, fontweight='bold', color='#e65100', ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff3e0', alpha=0.8, edgecolor='#ffcc80'))

ax.set_xlabel('Indice di Qualità della Vita (QoL Score 0-100)\n[Maggior punteggio = Meno notti, Meno reperibilità, Minore stress e rischio legale]', fontsize=11, fontweight='bold', labelpad=10)
ax.set_ylabel('Redditività Economica Potenziale Lorda Annua a 3-5 anni (in migliaia di €)\n[Stipendio SSN + Indennità + Libera Professione / Out-of-pocket stimata]', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('TRADE-OFF TRA QUALITÀ DELLA VITA E REDDITIVITÀ ECONOMICA POTENZIALE\nAnalisi per Specializzazione Medica in Italia', fontsize=13, fontweight='bold', pad=15)

# Legenda aree
for area_name, color in color_map.items():
    ax.scatter([], [], c=color, s=80, label=area_name, edgecolors='black', linewidth=0.5)
ax.legend(title='Area Disciplinare', loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#cccccc', fontsize=9)

ax.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
fig.savefig("reports/figures/qol_vs_rep_scatter.png", dpi=200)
plt.close(fig)
print("  -> Salvata reports/figures/qol_vs_rep_scatter.png")

# ==============================================================================
# FIGURA 3: Confronto dei 3 Scenari al 2031 per le Principali 15 Discipline
# ==============================================================================
print("Generazione Figura 3: Confronto 3 Scenari...")
key_disciplines = [
    "Medicina Generale (MMG*)", "Medicina d'emergenza-urgenza", "Chirurgia generale",
    "Malattie dell'apparato cardiovascolare", "Ortopedia e traumatologia", "Pediatria",
    "Ginecologia ed ostetricia", "Anestesia Rianimazione, Terapia Intensiva e del dolore",
    "Medicina interna", "Dermatologia e venereologia", "Oftalmologia", "Psichiatria",
    "Radiodiagnostica", "Geriatria", "Medicina dello sport e dell'esercizio fisico"
]

df_key = df_proj[(df_proj['tipo_territorio'] == 'Nazionale') & (df_proj['disciplina'].isin(key_disciplines))].copy()
piv_sc = df_key.pivot(index='disciplina', columns='scenario_id', values='isoo').loc[key_disciplines]

fig, ax = plt.subplots(figsize=(14, 8), dpi=200)
x_idx = np.arange(len(key_disciplines))
width = 0.26

r1 = ax.bar(x_idx - width, piv_sc['scenario_correttivo'], width, label='Scenario 3: Correttivo (Best Case)', color='#2e7d32', alpha=0.9)
r2 = ax.bar(x_idx, piv_sc['scenario_baseline'], width, label='Scenario 1: Baseline (Inerziale)', color='#1976d2', alpha=0.9)
r3 = ax.bar(x_idx + width, piv_sc['scenario_pletora'], width, label='Scenario 2: Pletora Grave (Worst Case)', color='#d32f2f', alpha=0.9)

ax.axhline(0.80, color='#2e7d32', linestyle='--', linewidth=1, alpha=0.7, label='Soglia Carenza (<0.80)')
ax.axhline(1.45, color='#d32f2f', linestyle='--', linewidth=1, alpha=0.7, label='Soglia Pletora (>1.45)')

ax.set_ylabel('Indice ISOO (Saturazione)', fontsize=11, fontweight='bold')
ax.set_title('SENSIBILITÀ DELL\'INDICE ISOO NEI 3 SCENARI AL 2031\nConfronto tra le Principali Discipline Medico-Chirurgiche', fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x_idx)
short_labels = [k.replace("Malattie dell'apparato ", "").replace("Medicina dello sport e dell'esercizio fisico", "Med. Sport").replace("Anestesia Rianimazione, Terapia Intensiva e del dolore", "Anestesia & Rian.").replace("Chirurgia generale", "Chir. Generale").replace("Ortopedia e traumatologia", "Ortopedia") for k in key_disciplines]
ax.set_xticklabels(short_labels, rotation=40, ha='right', fontsize=9)
ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cccccc', fontsize=9)
ax.grid(axis='y', linestyle=':', alpha=0.6)

plt.tight_layout()
fig.savefig("reports/figures/confronto_scenari.png", dpi=200)
plt.close(fig)
print("  -> Salvata reports/figures/confronto_scenari.png")

# ==============================================================================
# FIGURA 4: Generazione dei 52 Radar Chart per Singola Disciplina
# ==============================================================================
print("Generazione 52 Radar Charts per ciascuna specializzazione...")

categories = [
    'Opportunità SSN\n(Concorso)',
    'Potenziale Privato\n(Out-of-Pocket)',
    'Qualità della Vita\n(Orari & Notti)',
    'Serenità Legale\n(Basso Rischio)',
    'Flessibilità\nTerritoriale'
]
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1] # Chiudi il cerchio

def safe_filename(name):
    # sanitize for filename
    clean = name.lower().replace(" ", "_").replace("'", "").replace(",", "").replace("*", "").replace("(", "").replace(")", "").replace("-", "_").replace("/", "_")
    return clean

for _, row in df_nat_base.iterrows():
    name = row['disciplina']
    area = row['area']
    isoo = row['isoo']
    prob_ssn = row['probabilita_bando_ssn_pct']
    qol = row['qol_score_base']
    rep_priv = row['rep_privato_stimato']
    r_legale = row['classe_rischio_legale']
    
    # Valori normalizzati su scala 0-100 per il radar
    val_ssn = prob_ssn
    val_privato = min(100.0, (rep_priv / 70000.0) * 100.0)
    val_qol = qol
    val_legale = 100.0 - ((r_legale - 1) / 4.0 * 100.0) # 1=100%, 5=0%
    # Flessibilità territoriale: più c'è carenza diffusa ovunque, più è facile lavorare dove si vuole
    val_terr = max(20.0, min(100.0, (1.5 - isoo) * 80.0 + 30.0))
    
    values = [val_ssn, val_privato, val_qol, val_legale, val_terr]
    values += values[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), dpi=150)
    
    # Scegli colore di riempimento in base al semaforo
    if isoo < 0.80:
        fill_color = '#2e7d32'
    elif isoo <= 1.15:
        fill_color = '#43a047'
    elif isoo <= 1.45:
        fill_color = '#f57f17'
    else:
        fill_color = '#c62828'
        
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], categories, color='#333333', size=9, fontweight='semibold')
    ax.set_rlabel_position(0)
    plt.yticks([25, 50, 75, 100], ["25", "50", "75", "100"], color="#888888", size=8)
    plt.ylim(0, 100)
    
    ax.plot(angles, values, linewidth=2, linestyle='solid', color=fill_color)
    ax.fill(angles, values, color=fill_color, alpha=0.35)
    
    plt.title(f"{name}\nArea {area} | ISOO 2031: {isoo:.2f}", size=11, fontweight='bold', y=1.12, color='#111111')
    
    fname = f"reports/figures/radar/{safe_filename(name)}.png"
    plt.tight_layout()
    plt.savefig(fname, dpi=150)
    plt.close(fig)

print("  -> Generati tutti i 52 radar chart in reports/figures/radar/")
print("\n=== TUTTI GLI ASSET GRAFICI GENERATI CON SUCCESSO ===")
