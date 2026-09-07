from pypdf import PdfReader
import re
import pandas as pd

# 1. Parse Tabella 1 from anaao_fabbisogni_2018_2025.pdf
reader = PdfReader("data/raw/anaao_studies/anaao_fabbisogni_2018_2025.pdf")
text = reader.pages[5].extract_text() # page 6

rows = []
# Match lines like: Anatomia Patologica 621 466 1323 673 -208
# or Malattie dell'apparato cardiovascolare 2606 1954 5234 2663 -709
pattern = re.compile(r"^(.*?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([-\d]+)$")

for line in text.split("\n"):
    line = line.strip()
    m = pattern.match(line)
    if m:
        spec = m.group(1).strip()
        formati = int(m.group(2))
        nuovi_ssn = int(m.group(3))
        attivi_ssn = int(m.group(4))
        pensionamenti = int(m.group(5))
        ammanco = int(m.group(6))
        rows.append({
            "disciplina_anaao": spec,
            "specialisti_formati_2018_2025": formati,
            "nuovi_specialisti_ssn": nuovi_ssn,
            "specialisti_attivi_ssn_cat": attivi_ssn,
            "stima_pensionamenti_2018_2025": pensionamenti,
            "ammanco_specialisti": ammanco
        })

df_anaao = pd.DataFrame(rows)
print(f"Parsed {len(df_anaao)} major SSN specialties from Tabella 1:")
print(df_anaao.head(10))
print(f"Total attivi SSN in these major specialties: {df_anaao['specialisti_attivi_ssn_cat'].sum()}")
print(f"Total pensionamenti stimati: {df_anaao['stima_pensionamenti_2018_2025'].sum()}")
