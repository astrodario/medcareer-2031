import pandas as pd
import sqlite3

df = pd.read_parquet("data/processed/proiezioni_2031_multiscenario.parquet")

print("=== ANALISI DEI RISULTATI DELLE PROIEZIONI 2031 ===")

# Filtriamo il livello Nazionale
df_nat = df[df['tipo_territorio'] == 'Nazionale'].copy()

for sc in ['scenario_baseline', 'scenario_pletora', 'scenario_correttivo']:
    sub = df_nat[df_nat['scenario_id'] == sc]
    print(f"\n=======================================================")
    print(f" {sub['scenario_nome'].iloc[0].upper()} ")
    print(f"=======================================================")
    
    # Distribuzione semafori
    print("Distribuzione Verdetti:")
    print(sub['verdetto_carriera_2031'].value_counts().to_string())
    
    print("\n--- TOP 8 DISCIPLINE CON MAGGIORE CARENZA AL 2031 (ASSUNZIONE IMMEDIATA) ---")
    top_carenza = sub.sort_values('isoo', ascending=True)[['disciplina', 'area', 'isoo', 'saldo_netto_ssn', 'probabilita_bando_ssn_pct', 'verdetto_carriera_2031']].head(8)
    print(top_carenza.to_string())
    
    print("\n--- TOP 8 DISCIPLINE A RISCHIO PLETORA / SATURAZIONE AL 2031 ---")
    top_pletora = sub.sort_values('isoo', ascending=False)[['disciplina', 'area', 'isoo', 'saldo_netto_ssn', 'probabilita_bando_ssn_pct', 'verdetto_carriera_2031']].head(8)
    print(top_pletora.to_string())

# Analisi regionale comparata
print("\n=======================================================")
print(" CONFRONTO REGIONALE: ESEMPIO CARDIOLOGIA E MEU AL 2031 ")
print("=======================================================")
df_reg = df[(df['tipo_territorio'] == 'Regione') & (df['scenario_id'] == 'scenario_baseline')].copy()

for d in ["Malattie dell'apparato cardiovascolare", "Medicina d'emergenza-urgenza", "Dermatologia e venereologia", "Medicina Generale (MMG*)"]:
    sub_d = df_reg[df_reg['disciplina'] == d]
    print(f"\nDisciplina: {d}")
    print(sub_d[['territorio', 'isoo', 'probabilita_bando_ssn_pct', 'saldo_netto_ssn', 'verdetto_carriera_2031']].sort_values('isoo', ascending=True).head(5).to_string())
    print("  ... peggiori 3 regioni (più sature):")
    print(sub_d[['territorio', 'isoo', 'probabilita_bando_ssn_pct', 'saldo_netto_ssn', 'verdetto_carriera_2031']].sort_values('isoo', ascending=False).head(3).to_string())
