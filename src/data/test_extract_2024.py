import re
from pypdf import PdfReader
import pandas as pd

reader = PdfReader("data/raw/als_rinunce/ssm2024_suddivisione_contratti.pdf")

# In page 3 and 4 (0-indexed 2 and 3)
lines = reader.pages[2].extract_text().split("\n") + reader.pages[3].extract_text().split("\n")

records = []
pattern = re.compile(r"^\s*(.*?)\s+(\d+)\s+(\d+)\s+([-\d]+)\s+([-\d]+%)\s*$")

for line in lines:
    line = line.strip()
    m = pattern.match(line)
    if m:
        spec = m.group(1).strip()
        c2023 = int(m.group(2))
        c2024 = int(m.group(3))
        diff = int(m.group(4))
        pct = m.group(5)
        records.append({
            "disciplina_mur": spec,
            "contratti_statali_2023": c2023,
            "contratti_statali_2024": c2024,
            "differenza_statali": diff,
            "variazione_pct": pct
        })

df_pdf = pd.DataFrame(records)
print(f"Extracted {len(df_pdf)} specialties from 2024 comparison table")
print(df_pdf.head(10))
print(df_pdf.tail(5))
