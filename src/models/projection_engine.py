import sqlite3
import pandas as pd
import numpy as np

print("=== AVVIO MOTORE DI PROIEZIONE MULTI-SCENARIO 2026-2031 ===")

# 1. Carica il Database Unificato Baseline
df_base = pd.read_parquet("data/processed/database_unificato.parquet")
print(f"Caricato database baseline: {len(df_base)} record")

# 2. Definizione dei 3 Scenari
# Scenario 1: BASELINE (Trend inerziale, pensionamento a 67 anni, dimissioni fisiologiche)
# Scenario 2: PLETORA_GRAVE (Permanenza fino a 70 anni, contrazione turnover SSN -20%, contratti pieni)
# Scenario 3: CORRETTIVO (Taglio borse rami saturi -15%, potenziamento DM 77 territorio +15%, uscite anticipate)

scenarios = [
    {
        "id": "scenario_baseline",
        "nome": "Scenario 1: Baseline (Inerziale)",
        "descrizione": "Mantenimento trend attuale borse SSM, pensionamento ordinario 67 anni, ricambio 1:1 dei posti vacanti.",
        "molt_pensionamenti": 1.00,
        "molt_dimissioni_esodo": 1.00,
        "molt_fabbisogno_dm77": 1.00,
        "molt_borse_ssm": 1.00,
        "fattore_demografico_peso": 1.00
    },
    {
        "id": "scenario_pletora",
        "nome": "Scenario 2: Pletora Grave (Worst Case)",
        "descrizione": "Medici anziani restano fino a 70 anni (deroghe), blocco parziale turnover ASL (-15%), nessun taglio borse SSM.",
        "molt_pensionamenti": 0.80, # -20% uscite effettive a 5 anni per allungamento permanenza
        "molt_dimissioni_esodo": 0.90,
        "molt_fabbisogno_dm77": 0.85, # tagli regionali / ritardi PNRR
        "molt_borse_ssm": 1.05, # lievi aumenti ulteriori o saturazione
        "fattore_demografico_peso": 0.80 # minor traduzione del bisogno epidemiologico in assunzioni
    },
    {
        "id": "scenario_correttivo",
        "nome": "Scenario 3: Correttivo / Regolatorio (Best Case)",
        "descrizione": "Taglio selettivo borse nelle branche sature (-15%), pieno sblocco assunzioni territoriali DM 77 (+15%), uscite anticipate.",
        "molt_pensionamenti": 1.15, # prepensionamenti e incentivi all'esodo
        "molt_dimissioni_esodo": 1.10,
        "molt_fabbisogno_dm77": 1.20, # piena attuazione Case di Comunità
        "molt_borse_ssm": 0.90, # correzione delle pletore annunciate
        "fattore_demografico_peso": 1.20 # forte investimento pubblico sui bisogni dell'invecchiamento
    }
]

all_projections = []

for sc in scenarios:
    sc_id = sc['id']
    sc_nome = sc['nome']
    m_pens = sc['molt_pensionamenti']
    m_esodo = sc['molt_dimissioni_esodo']
    m_dm77 = sc['molt_fabbisogno_dm77']
    m_borse = sc['molt_borse_ssm']
    w_demo = sc['fattore_demografico_peso']
    
    for _, row in df_base.iterrows():
        disc = row['disciplina']
        area = row['area']
        durata = row['durata_anni']
        terr = row['territorio']
        tipo_terr = row['tipo_territorio']
        stock = row['stock_medici_attivi']
        contratti_5y = row['contratti_quinquennio_2026_2031']
        tasso_abbandono = row['tasso_abbandono_stimato']
        pens_base = row['pensionamenti_stimati_2026_2031']
        delta_demo = row['delta_demografico_target_pct']
        target_demo = row['target_demografico']
        qol_base = row['qol_score_base']
        rep_lorda = row['rep_lorda_annua']
        rep_privato = row['rep_privato_stimato']
        
        # 1. Calcolo Nuovi Diplomati Effettivi Coorte 2026-2031 nello scenario
        # Nello scenario correttivo, il taglio si applica soprattutto alle branche già sature (abbandono basso)
        if sc_id == "scenario_correttivo" and tasso_abbandono < 0.05:
            borse_sc = contratti_5y * 0.85 # taglio 15% mirato sulle branche a rischio pletora
        else:
            borse_sc = contratti_5y * m_borse
            
        nuovi_diplomati = round(borse_sc * (1 - tasso_abbandono))
        
        # 2. Calcolo Uscite Totali SSN (Pensionamenti + Esodo / Dimissioni volontarie)
        pens_scenario = round(pens_base * m_pens)
        # Dimissioni volontarie stimate: ~2.5% annuo dello stock su 5 anni = ~12.5% dello stock
        esodo_scenario = round(stock * 0.10 * m_esodo)
        uscite_totali_ssn = pens_scenario + esodo_scenario
        
        # 3. Ponderatore Demografico ISTAT
        # Moltiplicatore di fabbisogno legato all'invecchiamento o calo nascite
        # es. delta_demo = +10% over65 -> molt_demo = 1 + (0.10 * 0.5 * w_demo) = 1.05
        molt_demo = 1.0 + (delta_demo / 100.0) * 0.5 * w_demo
        
        # Fabbisogno DM 77 / Riforma Territorio:
        # Ha impatto forte su Cure Primarie (MMG*), Geriatria, Medicina Interna, Fisiatria, Igiene, Psichiatria
        bonus_dm77 = 1.0
        if disc in ["Medicina Generale (MMG*)", "Geriatria", "Medicina interna", "Medicina fisica e riabilitativa", "Psichiatria", "Medicina di comunità e delle cure primarie", "Igiene e medicina preventiva"]:
            bonus_dm77 = 1.0 + 0.15 * (m_dm77 - 1.0) if m_dm77 != 1.0 else 1.05
            
        # 4. Fabbisogno Netto Stimato SSN al 2031
        fabbisogno_netto_ssn = round(uscite_totali_ssn * molt_demo * bonus_dm77)
        
        # Capacità di assorbimento del settore privato (cliniche convenzionate AIOP/ARIS e studi)
        # Più è alto rep_privato, più il privato assorbe specialisti al di fuori del SSN
        quota_assorbimento_privato = min(0.65, (rep_privato / 150000.0) * 1.2)
        capacita_privato = round(nuovi_diplomati * quota_assorbimento_privato)
        
        # Fabbisogno Complessivo (SSN + Privato)
        fabbisogno_totale = fabbisogno_netto_ssn + capacita_privato
        
        # 5. Calcolo Indice ISOO (Indice di Saturazione e Opportunità Occupazionale)
        # Rapporto tra Nuovi Diplomati e Fabbisogno Totale
        if fabbisogno_totale > 0:
            isoo = round(nuovi_diplomati / fabbisogno_totale, 3)
        else:
            isoo = 2.0
            
        # Bilancio Algebrico Netto (Nuovi Diplomati - Fabbisogno SSN)
        saldo_netto_ssn = nuovi_diplomati - fabbisogno_netto_ssn
        
        # 6. Probabilità Percentuale di Vittoria Bando Ospedaliero SSN (0-100%)
        # Se fabbisogno_netto_ssn >= nuovi_diplomati, probabilità 95-99%
        # Se nuovi_diplomati > fabbisogno, la probabilità cala proporzionalmente
        quota_che_cerca_ssn = nuovi_diplomati * (1.0 - quota_assorbimento_privato * 0.7)
        if quota_che_cerca_ssn > 0:
            prob_bando_ssn = min(99.0, max(5.0, round((fabbisogno_netto_ssn / quota_che_cerca_ssn) * 100.0, 1)))
        else:
            prob_bando_ssn = 95.0
            
        # 7. Verdetto di Carriera al 2031
        if isoo < 0.80:
            verdetto = "Carenza Severa (Assunzione Immediata)"
            semaforo = "Verde Scuro"
            dettaglio_prospettiva = "Posti vacanti diffusi e concorsi spesso deserti; altissima probabilità di assunzione prima del titolo o subito dopo (Decreto Calabria)."
        elif isoo <= 1.15:
            verdetto = "Equilibrio Fisiologico"
            semaforo = "Verde Chiaro"
            dettaglio_prospettiva = "Buon bilanciamento tra uscite e nuovi specialisti; accesso regolare al SSN tramite concorso e spazio nel settore convenzionato."
        elif isoo <= 1.45:
            verdetto = "Competitivo / Rischio Saturazione"
            semaforo = "Giallo"
            dettaglio_prospettiva = "Graduatorie concorsuali affollate; tempi di attesa per tempo indeterminato SSN mediamente più lunghi; necessario appoggiarsi al privato accreditato."
        else:
            verdetto = "Pletora / Grave Saturazione"
            semaforo = "Rosso"
            dettaglio_prospettiva = "Forte esubero di specialisti rispetto alle posizioni ospedaliere disponibili al 2031; altissima concorrenza nei concorsi, sbocco quasi obbligato nella libera professione pura."
            
        all_projections.append({
            "scenario_id": sc_id,
            "scenario_nome": sc_nome,
            "disciplina": disc,
            "area": area,
            "durata_anni": durata,
            "territorio": terr,
            "tipo_territorio": tipo_terr,
            "stock_medici_attivi": stock,
            "pensionamenti_stimati_5y": pens_scenario,
            "esodo_dimissioni_stimato_5y": esodo_scenario,
            "uscite_totali_ssn_5y": uscite_totali_ssn,
            "moltiplicatore_demografico": round(molt_demo, 3),
            "fabbisogno_netto_ssn_2031": fabbisogno_netto_ssn,
            "capacita_assorbimento_privato": capacita_privato,
            "fabbisogno_totale_2031": fabbisogno_totale,
            "nuovi_diplomati_effettivi_5y": nuovi_diplomati,
            "saldo_netto_ssn": saldo_netto_ssn,
            "isoo": isoo,
            "probabilita_bando_ssn_pct": prob_bando_ssn,
            "verdetto_carriera_2031": verdetto,
            "semaforo": semaforo,
            "dettaglio_prospettiva": dettaglio_prospettiva,
            "qol_score_base": qol_base,
            "rep_lorda_annua": rep_lorda,
            "rep_privato_stimato": rep_privato
        })

df_proj = pd.DataFrame(all_projections)
print(f"\nProiezioni completate con successo:")
print(f"Totale record generati: {len(df_proj)} ({len(scenarios)} scenari x {len(df_base)} record base)")
print(f"Scenari: {df_proj['scenario_id'].unique().tolist()}")

# Salva in Parquet, CSV e SQLite
df_proj.to_parquet("data/processed/proiezioni_2031_multiscenario.parquet", index=False)
df_proj.to_csv("data/processed/proiezioni_2031_multiscenario.csv", index=False, encoding="utf-8-sig")

conn = sqlite3.connect("data/processed/database_unificato.sqlite")
df_proj.to_sql("proiezioni_2031", conn, if_exists="replace", index=False)
conn.close()

print("\nDataset proiezioni salvato con successo in:")
print("  - data/processed/proiezioni_2031_multiscenario.parquet")
print("  - data/processed/proiezioni_2031_multiscenario.csv")
print("  - data/processed/database_unificato.sqlite (tabella 'proiezioni_2031')")
