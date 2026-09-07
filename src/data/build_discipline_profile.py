import os
import json
import sqlite3
import pandas as pd
import numpy as np

os.makedirs("data/processed", exist_ok=True)

# 1. Caricamento Dati Demografici ISTAT
df_istat = pd.read_csv("data/processed/istat_demografia_2026_2031.csv")

# Standardizzazione nomi regioni (21 Regioni / PA)
regioni_standard = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana",
    "Umbria", "Valle d'Aosta", "Veneto", "P.A. Bolzano", "P.A. Trento"
]

# 2. Definizione delle 52 Discipline (51 Scuole SSM + MMG*)
discipline_data = [
    # Area Medica
    {"nome": "Allergologia ed immunologia clinica", "area": "Medica", "durata": 4, "target_demo": "totale", "notti_mese": 0.5, "rep_mese": 1.0, "ore_sett": 40, "rischio_legale": 1, "burnout": 40, "rep_privato_score": 7.0, "tariffa_visita_privata": 120},
    {"nome": "Dermatologia e venereologia", "area": "Medica", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.5, "ore_sett": 38, "rischio_legale": 1, "burnout": 30, "rep_privato_score": 10.0, "tariffa_visita_privata": 150},
    {"nome": "Ematologia", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 2.5, "rep_mese": 3.0, "ore_sett": 44, "rischio_legale": 2, "burnout": 65, "rep_privato_score": 4.5, "tariffa_visita_privata": 130},
    {"nome": "Endocrinologia e malattie del metabolismo", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 0.5, "rep_mese": 1.0, "ore_sett": 40, "rischio_legale": 1, "burnout": 45, "rep_privato_score": 8.0, "tariffa_visita_privata": 130},
    {"nome": "Gastroenterologia", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 2.5, "rep_mese": 3.5, "ore_sett": 45, "rischio_legale": 2, "burnout": 60, "rep_privato_score": 8.5, "tariffa_visita_privata": 140},
    {"nome": "Geriatria", "area": "Medica", "durata": 4, "target_demo": "over80", "notti_mese": 3.0, "rep_mese": 2.0, "ore_sett": 42, "rischio_legale": 1, "burnout": 60, "rep_privato_score": 6.0, "tariffa_visita_privata": 110},
    {"nome": "Malattie dell'apparato cardiovascolare", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 4.0, "rep_mese": 4.5, "ore_sett": 48, "rischio_legale": 3, "burnout": 70, "rep_privato_score": 9.5, "tariffa_visita_privata": 150},
    {"nome": "Malattie dell'apparato respiratorio", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 2.5, "rep_mese": 2.5, "ore_sett": 42, "rischio_legale": 2, "burnout": 60, "rep_privato_score": 7.5, "tariffa_visita_privata": 130},
    {"nome": "Malattie infettive e tropicali", "area": "Medica", "durata": 4, "target_demo": "totale", "notti_mese": 2.5, "rep_mese": 2.5, "ore_sett": 42, "rischio_legale": 2, "burnout": 65, "rep_privato_score": 4.0, "tariffa_visita_privata": 120},
    {"nome": "Medicina d'emergenza-urgenza", "area": "Medica", "durata": 4, "target_demo": "totale", "notti_mese": 6.5, "rep_mese": 1.0, "ore_sett": 48, "rischio_legale": 3, "burnout": 90, "rep_privato_score": 2.0, "tariffa_visita_privata": 100},
    {"nome": "Medicina di comunità e delle cure primarie", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 0.0, "rep_mese": 0.5, "ore_sett": 38, "rischio_legale": 1, "burnout": 45, "rep_privato_score": 4.0, "tariffa_visita_privata": 90},
    {"nome": "Medicina e cure palliative", "area": "Medica", "durata": 4, "target_demo": "over80", "notti_mese": 1.0, "rep_mese": 2.5, "ore_sett": 40, "rischio_legale": 1, "burnout": 65, "rep_privato_score": 4.0, "tariffa_visita_privata": 100},
    {"nome": "Medicina fisica e riabilitativa", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 0.5, "rep_mese": 1.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 40, "rep_privato_score": 8.0, "tariffa_visita_privata": 120},
    {"nome": "Medicina interna", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 4.0, "rep_mese": 2.5, "ore_sett": 45, "rischio_legale": 2, "burnout": 75, "rep_privato_score": 6.0, "tariffa_visita_privata": 120},
    {"nome": "Medicina nucleare", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 0.0, "rep_mese": 0.5, "ore_sett": 38, "rischio_legale": 1, "burnout": 40, "rep_privato_score": 3.0, "tariffa_visita_privata": 130},
    {"nome": "Medicina termale", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 0.0, "rep_mese": 0.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 30, "rep_privato_score": 4.0, "tariffa_visita_privata": 90},
    {"nome": "Nefrologia", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 2.5, "rep_mese": 3.5, "ore_sett": 44, "rischio_legale": 2, "burnout": 65, "rep_privato_score": 5.5, "tariffa_visita_privata": 130},
    {"nome": "Neurologia", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 3.0, "rep_mese": 3.0, "ore_sett": 44, "rischio_legale": 2, "burnout": 65, "rep_privato_score": 8.0, "tariffa_visita_privata": 140},
    {"nome": "Neuropsichiatria infantile", "area": "Medica", "durata": 4, "target_demo": "under15", "notti_mese": 1.0, "rep_mese": 1.5, "ore_sett": 40, "rischio_legale": 1, "burnout": 60, "rep_privato_score": 8.5, "tariffa_visita_privata": 130},
    {"nome": "Oncologia medica", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 2.0, "rep_mese": 2.5, "ore_sett": 44, "rischio_legale": 2, "burnout": 75, "rep_privato_score": 6.5, "tariffa_visita_privata": 140},
    {"nome": "Pediatria", "area": "Medica", "durata": 5, "target_demo": "under15", "notti_mese": 4.0, "rep_mese": 3.0, "ore_sett": 44, "rischio_legale": 2, "burnout": 65, "rep_privato_score": 8.0, "tariffa_visita_privata": 120},
    {"nome": "Psichiatria", "area": "Medica", "durata": 4, "target_demo": "totale", "notti_mese": 3.0, "rep_mese": 2.0, "ore_sett": 42, "rischio_legale": 2, "burnout": 80, "rep_privato_score": 8.5, "tariffa_visita_privata": 120},
    {"nome": "Radioterapia", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 0.5, "rep_mese": 1.5, "ore_sett": 40, "rischio_legale": 2, "burnout": 50, "rep_privato_score": 3.5, "tariffa_visita_privata": 130},
    {"nome": "Reumatologia", "area": "Medica", "durata": 4, "target_demo": "over65", "notti_mese": 0.5, "rep_mese": 1.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 45, "rep_privato_score": 7.5, "tariffa_visita_privata": 130},
    {"nome": "Medicina Generale (MMG*)", "area": "Cure Primarie*", "durata": 3, "target_demo": "over65", "notti_mese": 0.0, "rep_mese": 0.0, "ore_sett": 36, "rischio_legale": 2, "burnout": 60, "rep_privato_score": 4.0, "tariffa_visita_privata": 60},

    # Area Chirurgica
    {"nome": "Cardiochirurgia", "area": "Chirurgica", "durata": 5, "target_demo": "over65", "notti_mese": 4.5, "rep_mese": 6.0, "ore_sett": 54, "rischio_legale": 5, "burnout": 80, "rep_privato_score": 6.0, "tariffa_visita_privata": 180},
    {"nome": "Chirurgia generale", "area": "Chirurgica", "durata": 5, "target_demo": "over65", "notti_mese": 5.0, "rep_mese": 5.0, "ore_sett": 50, "rischio_legale": 4, "burnout": 75, "rep_privato_score": 7.0, "tariffa_visita_privata": 140},
    {"nome": "Chirurgia maxillo-facciale", "area": "Chirurgica", "durata": 5, "target_demo": "totale", "notti_mese": 3.0, "rep_mese": 4.0, "ore_sett": 46, "rischio_legale": 4, "burnout": 65, "rep_privato_score": 8.0, "tariffa_visita_privata": 160},
    {"nome": "Chirurgia pediatrica", "area": "Chirurgica", "durata": 5, "target_demo": "under15", "notti_mese": 3.5, "rep_mese": 4.5, "ore_sett": 46, "rischio_legale": 4, "burnout": 70, "rep_privato_score": 5.0, "tariffa_visita_privata": 140},
    {"nome": "Chirurgia plastica, ricostruttiva ed estetica", "area": "Chirurgica", "durata": 5, "target_demo": "totale", "notti_mese": 1.5, "rep_mese": 3.0, "ore_sett": 42, "rischio_legale": 5, "burnout": 50, "rep_privato_score": 10.0, "tariffa_visita_privata": 180},
    {"nome": "Chirurgia toracica", "area": "Chirurgica", "durata": 5, "target_demo": "over65", "notti_mese": 3.5, "rep_mese": 4.5, "ore_sett": 48, "rischio_legale": 4, "burnout": 70, "rep_privato_score": 5.5, "tariffa_visita_privata": 160},
    {"nome": "Chirurgia vascolare", "area": "Chirurgica", "durata": 5, "target_demo": "over65", "notti_mese": 4.0, "rep_mese": 5.0, "ore_sett": 48, "rischio_legale": 4, "burnout": 70, "rep_privato_score": 7.5, "tariffa_visita_privata": 150},
    {"nome": "Ginecologia ed ostetricia", "area": "Chirurgica", "durata": 5, "target_demo": "totale", "notti_mese": 4.5, "rep_mese": 4.5, "ore_sett": 48, "rischio_legale": 5, "burnout": 75, "rep_privato_score": 9.0, "tariffa_visita_privata": 140},
    {"nome": "Neurochirurgia", "area": "Chirurgica", "durata": 5, "target_demo": "over65", "notti_mese": 4.5, "rep_mese": 6.0, "ore_sett": 52, "rischio_legale": 5, "burnout": 80, "rep_privato_score": 6.5, "tariffa_visita_privata": 180},
    {"nome": "Oftalmologia", "area": "Chirurgica", "durata": 4, "target_demo": "over65", "notti_mese": 1.0, "rep_mese": 2.0, "ore_sett": 40, "rischio_legale": 3, "burnout": 45, "rep_privato_score": 10.0, "tariffa_visita_privata": 140},
    {"nome": "Ortopedia e traumatologia", "area": "Chirurgica", "durata": 5, "target_demo": "over65", "notti_mese": 4.0, "rep_mese": 5.0, "ore_sett": 48, "rischio_legale": 5, "burnout": 70, "rep_privato_score": 9.5, "tariffa_visita_privata": 150},
    {"nome": "Otorinolaringoiatria", "area": "Chirurgica", "durata": 4, "target_demo": "totale", "notti_mese": 2.0, "rep_mese": 3.0, "ore_sett": 42, "rischio_legale": 3, "burnout": 50, "rep_privato_score": 8.5, "tariffa_visita_privata": 130},
    {"nome": "Urologia", "area": "Chirurgica", "durata": 5, "target_demo": "over65", "notti_mese": 3.0, "rep_mese": 4.0, "ore_sett": 45, "rischio_legale": 3, "burnout": 60, "rep_privato_score": 8.5, "tariffa_visita_privata": 140},

    # Area Servizi Clinici
    {"nome": "Anatomia patologica", "area": "Servizi", "durata": 4, "target_demo": "over65", "notti_mese": 0.0, "rep_mese": 0.5, "ore_sett": 38, "rischio_legale": 2, "burnout": 50, "rep_privato_score": 3.5, "tariffa_visita_privata": 120},
    {"nome": "Anestesia Rianimazione, Terapia Intensiva e del dolore", "area": "Servizi", "durata": 5, "target_demo": "totale", "notti_mese": 5.5, "rep_mese": 4.5, "ore_sett": 48, "rischio_legale": 3, "burnout": 80, "rep_privato_score": 3.5, "tariffa_visita_privata": 130},
    {"nome": "Audiologia e foniatria", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.5, "ore_sett": 38, "rischio_legale": 1, "burnout": 35, "rep_privato_score": 7.0, "tariffa_visita_privata": 110},
    {"nome": "Farmacologia e Tossicologia Clinica", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.5, "ore_sett": 38, "rischio_legale": 1, "burnout": 35, "rep_privato_score": 3.0, "tariffa_visita_privata": 100},
    {"nome": "Genetica medica", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.5, "ore_sett": 38, "rischio_legale": 1, "burnout": 40, "rep_privato_score": 6.5, "tariffa_visita_privata": 130},
    {"nome": "Igiene e medicina preventiva", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 1.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 40, "rep_privato_score": 4.0, "tariffa_visita_privata": 100},
    {"nome": "Medicina del lavoro", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 35, "rep_privato_score": 8.5, "tariffa_visita_privata": 80},
    {"nome": "Medicina dello sport e dell'esercizio fisico", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.0, "ore_sett": 38, "rischio_legale": 2, "burnout": 35, "rep_privato_score": 8.5, "tariffa_visita_privata": 70},
    {"nome": "Medicina legale", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 1.0, "ore_sett": 38, "rischio_legale": 2, "burnout": 45, "rep_privato_score": 9.0, "tariffa_visita_privata": 200},
    {"nome": "Microbiologia e virologia", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 1.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 40, "rep_privato_score": 2.5, "tariffa_visita_privata": 100},
    {"nome": "Patologia Clinica e Biochimica Clinica", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.5, "rep_mese": 1.5, "ore_sett": 38, "rischio_legale": 1, "burnout": 45, "rep_privato_score": 3.0, "tariffa_visita_privata": 100},
    {"nome": "Radiodiagnostica", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 2.5, "rep_mese": 3.5, "ore_sett": 42, "rischio_legale": 3, "burnout": 65, "rep_privato_score": 8.0, "tariffa_visita_privata": 130},
    {"nome": "Scienza dell'alimentazione", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 35, "rep_privato_score": 8.0, "tariffa_visita_privata": 110},
    {"nome": "Statistica sanitaria e Biometria", "area": "Servizi", "durata": 4, "target_demo": "totale", "notti_mese": 0.0, "rep_mese": 0.0, "ore_sett": 38, "rischio_legale": 1, "burnout": 30, "rep_privato_score": 3.0, "tariffa_visita_privata": 120}
]

df_disc = pd.DataFrame(discipline_data)
print(f"Discipline definite: {len(df_disc)} (51 Scuole SSM + MMG*)")

# 3. Calcolo Formula QoL (0-100)
# Pesi: Notti 30%, Reperibilità 20%, Straordinari (ore extra vs 38) 20%, Rischio legale 15%, Burnout 15%
def calcola_qol(row):
    score_notti = np.clip(row['notti_mese'] / 7.0 * 100, 0, 100)
    score_rep = np.clip(row['rep_mese'] / 6.0 * 100, 0, 100)
    ore_extra = max(0, row['ore_sett'] - 38)
    score_ore = np.clip(ore_extra / 16.0 * 100, 0, 100)
    score_legale = (row['rischio_legale'] - 1) / 4.0 * 100
    score_burnout = row['burnout']
    
    penalita = (0.30 * score_notti +
                0.20 * score_rep +
                0.20 * score_ore +
                0.15 * score_legale +
                0.15 * score_burnout)
    return round(100.0 - penalita, 1)

df_disc['qol_score_base'] = df_disc.apply(calcola_qol, axis=1)

# 4. Modello Economico REP (Redditività Economica Potenziale a 3-5 anni)
# Canale SSN Base: 76.000 € lordi base
# Indennità Pronto Soccorso per MEU: +8.500 €
# Turni / Notti: +600 € a notte media/mese annualizzata
# Privato / Out-of-pocket: rep_privato_score (1-10) * volume stimato * tariffa
def calcola_rep(row):
    ssn_base = 76000
    if "emergenza" in row['nome'].lower():
        ssn_base += 8500
    indennita_turni = row['notti_mese'] * 12 * 70  # ~70€ indennità oraria/turno notte
    
    # Canale out-of-pocket stimato annuo lordo
    # score 1 = ~2.000€, score 10 = ~70.000€
    privato_stimato = (row['rep_privato_score'] ** 1.8) * 1100
    
    if "MMG" in row['nome']:
        # Medico di medicina generale convenzionato massimalista
        rep_totale_lorda = 110000
        netto_stimato = 58000
    else:
        rep_totale_lorda = ssn_base + indennita_turni + privato_stimato
        # Netto stimato IRPEF progressiva media ~43% + addizionali regionali
        netto_stimato = rep_totale_lorda * 0.55
        
    return pd.Series([round(rep_totale_lorda, -2), round(netto_stimato, -2), round(privato_stimato, -2)],
                     index=['rep_lorda_annua_stimata', 'rep_netta_annua_stimata', 'rep_privato_out_of_pocket'])

df_disc[['rep_lorda_annua_stimata', 'rep_netta_annua_stimata', 'rep_privato_out_of_pocket']] = df_disc.apply(calcola_rep, axis=1)

print("\nTop 5 QoL:")
print(df_disc.sort_values('qol_score_base', ascending=False)[['nome', 'qol_score_base', 'rischio_legale', 'notti_mese']].head(5))

print("\nTop 5 REP (Reddito Potenziale):")
print(df_disc.sort_values('rep_lorda_annua_stimata', ascending=False)[['nome', 'rep_lorda_annua_stimata', 'rep_netta_annua_stimata', 'rep_privato_out_of_pocket']].head(5))

df_disc.to_csv("data/processed/discipline_caratteristiche.csv", index=False, encoding="utf-8-sig")
print("\nSalvate caratteristiche discipline in data/processed/discipline_caratteristiche.csv")
