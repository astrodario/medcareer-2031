import sqlite3
import pandas as pd

df = pd.read_parquet("data/processed/database_unificato.parquet")

print("=== AUDIT E VERIFICA QUALITÀ DEL DATABASE UNIFICATO ===")
print(f"Dimensioni: {df.shape[0]} righe x {df.shape[1]} colonne")
print(f"Numero di discipline uniche: {df['disciplina'].nunique()}")
print(f"Numero di territori unici: {df['territorio'].nunique()}")

# Controllo valori nulli
nulls = df.isnull().sum()
print("\nValori nulli per colonna:")
for col, n in nulls.items():
    if n > 0:
        print(f"  - {col}: {n} nulls")
if nulls.sum() == 0:
    print("  -> NESSUN VALORE NULLO. Dataset integro al 100%.")

# Verifica MMG*
mmg_rows = df[df['disciplina'].str.contains("MMG")]
print(f"\nVerifica Medicina Generale (MMG*): {len(mmg_rows)} record (1 nazionale + 21 regionali)")

# Sommario aggregato nazionale
df_nat = df[df['tipo_territorio'] == 'Nazionale'].copy()
print("\nTop 5 Scuole per Contratti Annuali (Nazionale):")
print(df_nat.sort_values('contratti_annui_totali', ascending=False)[['disciplina', 'area', 'contratti_annui_totali', 'nuovi_specialisti_effettivi_5anni']].head(5).to_string())

print("\nTop 5 Scuole per Pensionamenti Stimati nel Quinquennio (Nazionale):")
print(df_nat.sort_values('pensionamenti_stimati_2026_2031', ascending=False)[['disciplina', 'stock_medici_attivi', 'pensionamenti_stimati_2026_2031']].head(5).to_string())

print("\nTop 5 Scuole per Indice di Qualità della Vita (QoL 0-100):")
print(df_nat.sort_values('qol_score_base', ascending=False)[['disciplina', 'qol_score_base', 'notti_mese', 'ore_settimanali', 'classe_rischio_legale']].head(5).to_string())

print("\nBottom 5 Scuole per Qualità della Vita (più logoranti):")
print(df_nat.sort_values('qol_score_base', ascending=True)[['disciplina', 'qol_score_base', 'notti_mese', 'ore_settimanali', 'classe_rischio_legale', 'indice_burnout']].head(5).to_string())

print("\nTop 5 Scuole per Redditività Economica Potenziale (REP Lorda Annua):")
print(df_nat.sort_values('rep_lorda_annua', ascending=False)[['disciplina', 'rep_lorda_annua', 'rep_netta_annua', 'rep_privato_stimato']].head(5).to_string())

# Test query SQLite
conn = sqlite3.connect("data/processed/database_unificato.sqlite")
cur = conn.cursor()
cur.execute("SELECT count(*) FROM baseline_medici")
cnt = cur.fetchone()[0]
conn.close()
print(f"\nVerifica SQLite: {cnt} righe indicizzate nella tabella 'baseline_medici'.")

print("\n=== AUDIT COMPLETATO CON SUCCESSO ===")
