import os
import sqlite3
import pandas as pd
import numpy as np

os.makedirs("data/processed", exist_ok=True)

# 1. Carica caratteristiche discipline
df_disc = pd.read_csv("data/processed/discipline_caratteristiche.csv")

# 2. Carica demografia ISTAT
df_dem = pd.read_csv("data/processed/istat_demografia_2026_2031.csv")

# Mappa per uniformare i nomi ISTAT alle 21 Regioni / PA
istat_to_std = {
    "Provincia autonoma di Bolzano": "P.A. Bolzano",
    "Provincia autonoma di Trento": "P.A. Trento",
    "Valle d Aosta-Vallee d Aoste": "Valle d'Aosta"
}
df_dem['regione_std'] = df_dem['regione'].replace(istat_to_std)

regioni_21 = [
    "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
    "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardia", "Marche",
    "Molise", "Piemonte", "Puglia", "Sardegna", "Sicilia", "Toscana",
    "Umbria", "Valle d'Aosta", "Veneto", "P.A. Bolzano", "P.A. Trento"
]

# Quote demografiche regionali (popolazione 2026 su Italia totale)
df_dem_reg = df_dem[df_dem['regione_std'].isin(regioni_21)].copy()
pop_italia = df_dem_reg['pop_totale_2026'].sum()
df_dem_reg['peso_popolazione'] = df_dem_reg['pop_totale_2026'] / pop_italia

demo_dict = df_dem_reg.set_index('regione_std').to_dict(orient='index')

# Contratti Statali Nazionali di Riferimento (Media SSM 2023-2024 / MUR)
contratti_statali_base = {
    "Allergologia ed immunologia clinica": 85,
    "Anatomia patologica": 175,
    "Anestesia Rianimazione, Terapia Intensiva e del dolore": 1540,
    "Audiologia e foniatria": 35,
    "Cardiochirurgia": 95,
    "Chirurgia generale": 690,
    "Chirurgia maxillo-facciale": 55,
    "Chirurgia pediatrica": 60,
    "Chirurgia plastica, ricostruttiva ed estetica": 110,
    "Chirurgia toracica": 90,
    "Chirurgia vascolare": 115,
    "Dermatologia e venereologia": 125,
    "Ematologia": 204,
    "Endocrinologia e malattie del metabolismo": 200,
    "Farmacologia e Tossicologia Clinica": 105,
    "Gastroenterologia": 206,
    "Genetica medica": 70,
    "Geriatria": 390,
    "Ginecologia ed ostetricia": 525,
    "Igiene e medicina preventiva": 560,
    "Malattie dell'apparato cardiovascolare": 580,
    "Malattie dell'apparato respiratorio": 265,
    "Malattie infettive e tropicali": 250,
    "Medicina d'emergenza-urgenza": 925,
    "Medicina del lavoro": 190,
    "Medicina dello sport e dell'esercizio fisico": 88,
    "Medicina di comunità e delle cure primarie": 125,
    "Medicina e cure palliative": 140,
    "Medicina fisica e riabilitativa": 340,
    "Medicina interna": 810,
    "Medicina legale": 155,
    "Medicina nucleare": 90,
    "Medicina termale": 5,
    "Microbiologia e virologia": 110,
    "Nefrologia": 320,
    "Neurochirurgia": 112,
    "Neurologia": 310,
    "Neuropsichiatria infantile": 215,
    "Oftalmologia": 220,
    "Oncologia medica": 310,
    "Ortopedia e traumatologia": 472,
    "Otorinolaringoiatria": 185,
    "Patologia Clinica e Biochimica Clinica": 265,
    "Pediatria": 812,
    "Psichiatria": 520,
    "Radiodiagnostica": 655,
    "Radioterapia": 170,
    "Reumatologia": 120,
    "Scienza dell'alimentazione": 60,
    "Statistica sanitaria e Biometria": 40,
    "Urologia": 250,
    "Medicina Generale (MMG*)": 2700
}

# Tasso Storico di Non Assegnazione / Abbandono (%) (dati ALS e ANAAO)
tassi_abbandono = {
    "Medicina d'emergenza-urgenza": 0.48,
    "Medicina termale": 0.50,
    "Statistica sanitaria e Biometria": 0.45,
    "Farmacologia e Tossicologia Clinica": 0.42,
    "Patologia Clinica e Biochimica Clinica": 0.40,
    "Microbiologia e virologia": 0.38,
    "Radioterapia": 0.35,
    "Anatomia patologica": 0.30,
    "Medicina di comunità e delle cure primarie": 0.32,
    "Medicina e cure palliative": 0.28,
    "Chirurgia generale": 0.18,
    "Chirurgia toracica": 0.15,
    "Nefrologia": 0.15,
    "Geriatria": 0.16,
    "Igiene e medicina preventiva": 0.12,
    "Medicina interna": 0.12,
    "Anestesia Rianimazione, Terapia Intensiva e del dolore": 0.14,
    "Psichiatria": 0.10,
    "Medicina del lavoro": 0.10,
    "Medicina Generale (MMG*)": 0.12,
    "Chirurgia vascolare": 0.08,
    "Audiologia e foniatria": 0.08,
    "Urologia": 0.05,
    "Ematologia": 0.05,
    "Oncologia medica": 0.05,
    "Malattie infettive e tropicali": 0.05,
    "Malattie dell'apparato respiratorio": 0.05,
    "Ortopedia e traumatologia": 0.04,
    "Ginecologia ed ostetricia": 0.04,
    "Pediatria": 0.03,
    "Neurochirurgia": 0.04,
    "Cardiochirurgia": 0.04,
    "Neurologia": 0.03,
    "Radiodiagnostica": 0.03,
    "Gastroenterologia": 0.02,
    "Endocrinologia e malattie del metabolismo": 0.02,
    "Otorinolaringoiatria": 0.03,
    "Medicina fisica e riabilitativa": 0.03,
    "Chirurgia pediatrica": 0.04,
    "Chirurgia maxillo-facciale": 0.03,
    "Neuropsichiatria infantile": 0.02,
    "Reumatologia": 0.02,
    "Scienza dell'alimentazione": 0.03,
    "Genetica medica": 0.04,
    "Allergologia ed immunologia clinica": 0.02,
    "Dermatologia e venereologia": 0.01,
    "Oftalmologia": 0.01,
    "Chirurgia plastica, ricostruttiva ed estetica": 0.01,
    "Malattie dell'apparato cardiovascolare": 0.01,
    "Medicina legale": 0.03,
    "Medicina dello sport e dell'esercizio fisico": 0.03,
    "Medicina nucleare": 0.05
}

# Stock Attivo SSN Nazionale (CAT MEF / ANAAO)
stock_nazionale_ssn = {
    "Anestesia Rianimazione, Terapia Intensiva e del dolore": 11500,
    "Medicina interna": 8000,
    "Chirurgia generale": 7000,
    "Medicina d'emergenza-urgenza": 6500,
    "Pediatria": 6200,
    "Radiodiagnostica": 6200,
    "Malattie dell'apparato cardiovascolare": 5400,
    "Ginecologia ed ostetricia": 5000,
    "Psichiatria": 4800,
    "Ortopedia e traumatologia": 4200,
    "Igiene e medicina preventiva": 3000,
    "Neurologia": 2400,
    "Nefrologia": 2200,
    "Gastroenterologia": 2000,
    "Oncologia medica": 2100,
    "Oftalmologia": 1900,
    "Otorinolaringoiatria": 1800,
    "Urologia": 1850,
    "Patologia Clinica e Biochimica Clinica": 1600,
    "Medicina fisica e riabilitativa": 1650,
    "Malattie dell'apparato respiratorio": 1500,
    "Ematologia": 1450,
    "Malattie infettive e tropicali": 1400,
    "Anatomia patologica": 1380,
    "Geriatria": 1350,
    "Endocrinologia e malattie del metabolismo": 1100,
    "Neuropsichiatria infantile": 1200,
    "Dermatologia e venereologia": 950,
    "Chirurgia vascolare": 900,
    "Neurochirurgia": 880,
    "Cardiochirurgia": 750,
    "Radioterapia": 750,
    "Chirurgia plastica, ricostruttiva ed estetica": 700,
    "Medicina legale": 650,
    "Chirurgia toracica": 600,
    "Medicina nucleare": 550,
    "Medicina del lavoro": 520,
    "Reumatologia": 500,
    "Farmacologia e Tossicologia Clinica": 450,
    "Microbiologia e virologia": 400,
    "Chirurgia pediatrica": 360,
    "Chirurgia maxillo-facciale": 350,
    "Medicina e cure palliative": 400,
    "Medicina di comunità e delle cure primarie": 350,
    "Audiologia e foniatria": 250,
    "Allergologia ed immunologia clinica": 220,
    "Genetica medica": 200,
    "Statistica sanitaria e Biometria": 150,
    "Scienza dell'alimentazione": 120,
    "Medicina dello sport e dell'esercizio fisico": 100,
    "Medicina termale": 20,
    "Medicina Generale (MMG*)": 39366
}

records = []

for _, disc in df_disc.iterrows():
    nome = disc['nome']
    area = disc['area']
    durata = disc['durata']
    target_demo = disc['target_demo']
    qol_base = disc['qol_score_base']
    rep_lorda = disc['rep_lorda_annua_stimata']
    rep_netta = disc['rep_netta_annua_stimata']
    rep_privato = disc['rep_privato_out_of_pocket']
    notti = disc['notti_mese']
    rep_oncall = disc['rep_mese']
    ore_sett = disc['ore_sett']
    rischio_legale = disc['rischio_legale']
    burnout = disc['burnout']
    
    contratti_nat = contratti_statali_base.get(nome, 100)
    tasso_abbandono = tassi_abbandono.get(nome, 0.05)
    stock_nat = stock_nazionale_ssn.get(nome, 1000)
    
    # 1. Record Nazionale
    records.append({
        "disciplina": nome,
        "area": area,
        "durata_anni": durata,
        "territorio": "Italia (Nazionale)",
        "tipo_territorio": "Nazionale",
        "contratti_annui_totali": contratti_nat,
        "contratti_quinquennio_2026_2031": contratti_nat * 5,
        "tasso_abbandono_stimato": tasso_abbandono,
        "nuovi_specialisti_effettivi_5anni": round(contratti_nat * 5 * (1 - tasso_abbandono)),
        "stock_medici_attivi": stock_nat,
        "quota_pensionandi_60plus": 0.38 if "MMG" not in nome else 0.54,
        "pensionamenti_stimati_2026_2031": round(stock_nat * (0.38 if "MMG" not in nome else 0.54)),
        "delta_demografico_target_pct": 8.5 if target_demo == "over65" else (-10.2 if target_demo == "under15" else -0.5),
        "target_demografico": target_demo,
        "qol_score_base": qol_base,
        "notti_mese": notti,
        "reperibilita_mese": rep_oncall,
        "ore_settimanali": ore_sett,
        "classe_rischio_legale": rischio_legale,
        "indice_burnout": burnout,
        "rep_lorda_annua": rep_lorda,
        "rep_netta_annua": rep_netta,
        "rep_privato_stimato": rep_privato
    })
    
    # 2. Record per ciascuna delle 21 Regioni / PA
    for reg in regioni_21:
        d_info = demo_dict[reg]
        peso_pop = d_info['peso_popolazione']
        
        contratti_reg = max(0, round(contratti_nat * peso_pop))
        if contratti_nat >= 20 and contratti_reg == 0 and peso_pop > 0.015:
            contratti_reg = 1
        
        stock_reg = max(1, round(stock_nat * peso_pop))
        
        fattore_anzianita = 1.05 if reg in ["Liguria", "Molise", "Basilicata", "Calabria", "Sicilia"] else (0.95 if reg in ["Lombardia", "Veneto", "P.A. Bolzano", "P.A. Trento"] else 1.0)
        quota_pens = (0.38 if "MMG" not in nome else 0.54) * fattore_anzianita
        pens_reg = round(stock_reg * quota_pens)
        
        if target_demo == "over65":
            delta_demo = d_info['delta_over65_pct']
        elif target_demo == "over80":
            delta_demo = d_info['delta_over80_pct']
        elif target_demo == "under15":
            delta_demo = d_info['delta_under15_pct']
        else:
            delta_demo = d_info['delta_pop_totale_pct']
            
        records.append({
            "disciplina": nome,
            "area": area,
            "durata_anni": durata,
            "territorio": reg,
            "tipo_territorio": "Regione",
            "contratti_annui_totali": contratti_reg,
            "contratti_quinquennio_2026_2031": contratti_reg * 5,
            "tasso_abbandono_stimato": tasso_abbandono,
            "nuovi_specialisti_effettivi_5anni": round(contratti_reg * 5 * (1 - tasso_abbandono)),
            "stock_medici_attivi": stock_reg,
            "quota_pensionandi_60plus": round(quota_pens, 3),
            "pensionamenti_stimati_2026_2031": pens_reg,
            "delta_demografico_target_pct": round(delta_demo, 2),
            "target_demografico": target_demo,
            "qol_score_base": qol_base,
            "notti_mese": notti,
            "reperibilita_mese": rep_oncall,
            "ore_settimanali": ore_sett,
            "classe_rischio_legale": rischio_legale,
            "indice_burnout": burnout,
            "rep_lorda_annua": rep_lorda,
            "rep_netta_annua": rep_netta,
            "rep_privato_stimato": rep_privato
        })

df_unified = pd.DataFrame(records)
print(f"\nDatabase Unificato costruito con successo:")
print(f"Totale record: {len(df_unified)} (52 nazionali + {52*21} regionali = {len(df_unified)})")
print(f"Discipline: {df_unified['disciplina'].nunique()}")
print(f"Territori: {df_unified['territorio'].nunique()} (21 Regioni/PA + Nazionale)")

# Salva in Parquet, CSV e SQLite
df_unified.to_parquet("data/processed/database_unificato.parquet", index=False)
df_unified.to_csv("data/processed/database_unificato.csv", index=False, encoding="utf-8-sig")

conn = sqlite3.connect("data/processed/database_unificato.sqlite")
df_unified.to_sql("baseline_medici", conn, if_exists="replace", index=False)
conn.close()

print("\nDatabase salvato con successo in:")
print("  - data/processed/database_unificato.parquet")
print("  - data/processed/database_unificato.csv")
print("  - data/processed/database_unificato.sqlite")
