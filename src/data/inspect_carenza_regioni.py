from pypdf import PdfReader

reader = PdfReader("data/raw/anaao_studies/anaao_carenza_regioni_2019.pdf")
print("Pages:", len(reader.pages))
for i in range(len(reader.pages)):
    txt = reader.pages[i].extract_text()
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    print(f"Page {i+1}: {len(lines)} lines. First line: {lines[0] if lines else ''}")
    # Print lines with numbers or region names
    for l in lines:
        if any(r in l.upper() for r in ["PIEMONTE", "LOMBARDIA", "VENETO", "EMILIA", "TOSCANA", "LAZIO", "CAMPANIA", "PUGLIA", "SICILIA"]):
            if any(c.isdigit() for c in l):
                print(f"  [P{i+1}] {l}")
