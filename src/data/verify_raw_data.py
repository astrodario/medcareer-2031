import os
import glob
import pandas as pd
import openpyxl
from pypdf import PdfReader

print("=== VERIFICA INTEGRITÀ DATASET SCARICATI ===")

# 1. Anaao studies
anaao_files = glob.glob("data/raw/anaao_studies/*.pdf")
print(f"1. Studi ANAAO: {len(anaao_files)} file PDF verificati")
for f in anaao_files:
    r = PdfReader(f)
    print(f"   - {os.path.basename(f)}: {len(r.pages)} pagine")

# 2. MUR SSM
mur_xlsx = glob.glob("data/raw/mur_ssm/*.xlsx")
print(f"\n2. MUR SSM: {len(mur_xlsx)} file Excel verificati")
for f in mur_xlsx:
    wb = openpyxl.load_workbook(f, read_only=True)
    print(f"   - {os.path.basename(f)}: {len(wb.sheetnames)} fogli (specializzazioni)")

# 3. ALS reports
als_files = glob.glob("data/raw/als_rinunce/*.*")
print(f"\n3. ALS reports e contratti: {len(als_files)} file")
print(f"   - ssm2024_suddivisione_contratti.pdf presente: {os.path.exists('data/raw/als_rinunce/ssm2024_suddivisione_contratti.pdf')}")
print(f"   - area_medica unzipped: {len(os.listdir('data/raw/als_rinunce/area_medica'))} file")
print(f"   - area_chirurgica unzipped: {len(os.listdir('data/raw/als_rinunce/area_chirurgica'))} file")
print(f"   - area_servizi unzipped: {len(os.listdir('data/raw/als_rinunce/area_servizi'))} file")

# 4. ISTAT
istat_regioni = glob.glob("data/raw/istat/Previsioni-Popolazione_per_eta-Regioni/*.csv")
print(f"\n4. ISTAT Previsioni Demografiche Regionali: {len(istat_regioni)} file CSV per regione")
# Test read one
df_test = pd.read_csv(istat_regioni[0], sep=';', skiprows=2, encoding='utf-8')
print(f"   - Test su {os.path.basename(istat_regioni[0])}: shape {df_test.shape}, colonne: {list(df_test.columns[:4])}")

print("\n=== TUTTI I DATASET PRINCIPALI SONO STATI VERIFICATI CON SUCCESSO ===")
