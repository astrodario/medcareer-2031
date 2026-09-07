import os
import glob
import pandas as pd
import re

folder = "data/raw/istat/Previsioni-Popolazione_per_eta-Regioni"
files = glob.glob(os.path.join(folder, "*.csv"))

results = []

region_name_cleaner = {
    "Provincia_Autonoma_Bolzano_Bozen": "P.A. Bolzano",
    "Provincia_Autonoma_Trento": "P.A. Trento",
    "Valle_dAosta": "Valle d'Aosta",
    "Friuli-Venezia_Giulia": "Friuli-Venezia Giulia",
    "Emilia-Romagna": "Emilia-Romagna"
}

for f in files:
    basename = os.path.basename(f)
    m = re.search(r"it-Popolazione_per_eta_-_(?:Regione_)?(.*)\.csv", basename)
    if not m:
        continue
    raw_reg = m.group(1)
    if raw_reg == "Italia":
        reg_clean = "Italia"
    elif raw_reg in region_name_cleaner:
        reg_clean = region_name_cleaner[raw_reg]
    else:
        reg_clean = raw_reg.replace("_", " ")

    df = pd.read_csv(f, sep=";", skiprows=2, index_col=False, encoding="utf-8")
    df['Anno'] = pd.to_numeric(df['Anno'], errors='coerce')
    df_years = df[df['Anno'].isin([2026, 2031])].copy()
    
    col_val = [c for c in df_years.columns if "mediano" in c.lower()][0]
    df_years['Valore'] = pd.to_numeric(df_years[col_val], errors='coerce')
    
    # We take Sesso == 'Totale'
    df_tot = df_years[df_years['Sesso'] == 'Totale'].copy()
    
    # Exclude row where Età == 'Totale'
    df_ages = df_tot[df_tot['Età'] != 'Totale'].copy()
    df_ages['Eta_num'] = df_ages['Età'].astype(str).str.extract(r'(\d+)').astype(float)
    
    for anno in [2026, 2031]:
        sub = df_ages[df_ages['Anno'] == anno]
        pop_tot = sub['Valore'].sum()
        pop_u15 = sub[sub['Eta_num'] < 15]['Valore'].sum()
        pop_15_64 = sub[(sub['Eta_num'] >= 15) & (sub['Eta_num'] < 65)]['Valore'].sum()
        pop_65p = sub[sub['Eta_num'] >= 65]['Valore'].sum()
        pop_80p = sub[sub['Eta_num'] >= 80]['Valore'].sum()
        
        results.append({
            "regione": reg_clean,
            "anno": anno,
            "pop_totale": pop_tot,
            "pop_under15": pop_u15,
            "pop_15_64": pop_15_64,
            "pop_over65": pop_65p,
            "pop_over80": pop_80p
        })

df_res = pd.DataFrame(results)

piv = df_res.pivot(index="regione", columns="anno")
piv.columns = [f"{col}_{yr}" for col, yr in piv.columns]
piv = piv.reset_index()

piv['delta_pop_totale_pct'] = (piv['pop_totale_2031'] - piv['pop_totale_2026']) / piv['pop_totale_2026'] * 100
piv['delta_under15_pct'] = (piv['pop_under15_2031'] - piv['pop_under15_2026']) / piv['pop_under15_2026'] * 100
piv['delta_over65_pct'] = (piv['pop_over65_2031'] - piv['pop_over65_2026']) / piv['pop_over65_2026'] * 100
piv['delta_over80_pct'] = (piv['pop_over80_2031'] - piv['pop_over80_2026']) / piv['pop_over80_2026'] * 100

print(f"Demographics calculated successfully for {len(piv)} territories:")
print(piv[['regione', 'pop_totale_2026', 'delta_pop_totale_pct', 'delta_under15_pct', 'delta_over65_pct']].to_string())

piv.to_csv("data/processed/istat_demografia_2026_2031.csv", index=False, encoding="utf-8-sig")
print("\nSaved to data/processed/istat_demografia_2026_2031.csv")
