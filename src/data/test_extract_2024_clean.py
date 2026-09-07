import re
from pypdf import PdfReader
import pandas as pd

reader = PdfReader("data/raw/als_rinunce/ssm2024_suddivisione_contratti.pdf")
lines = reader.pages[2].extract_text().split("\n") + reader.pages[3].extract_text().split("\n")

records = []
pattern = re.compile(r"^(.*?)\s+(\d+)\s+(\d+)\s+([-\d]+)\s+([-\d]+%)\s*$")

pending_name = ""
for line in lines:
    line = line.strip()
    if not line or "POSTI STATALI" in line or "CONFRONTO" in line or "Associazione" in line or "Sito:" in line or "Email:" in line or "SUDDIVISI" in line:
        continue
    if "SPECIALIZZAZIONE" in line:
        continue
    m = pattern.match(line)
    if m:
        name_part = m.group(1).strip()
        full_name = f"{pending_name} {name_part}".strip() if pending_name else name_part
        c2023 = int(m.group(2))
        c2024 = int(m.group(3))
        diff = int(m.group(4))
        pct = m.group(5)
        records.append({
            "disciplina_mur": full_name,
            "contratti_statali_2023": c2023,
            "contratti_statali_2024": c2024,
            "differenza_statali": diff,
            "variazione_pct": pct
        })
        pending_name = ""
    else:
        # Might be the first line of a wrapped specialty name
        if not any(k in line.lower() for k in ["la soluzione", "avendo a", "facendo", "diminuito", "l’entit"]):
            pending_name = line

df_pdf = pd.DataFrame(records)
print(f"Extracted {len(df_pdf)} specialties cleanly:")
for idx, row in df_pdf.iterrows():
    if "anestesia" in row['disciplina_mur'].lower():
        print(f"Row {idx}: {row['disciplina_mur']} -> 2023: {row['contratti_statali_2023']}, 2024: {row['contratti_statali_2024']}")
print(f"Total rows: {len(df_pdf)}")
