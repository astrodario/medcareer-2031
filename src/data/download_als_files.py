import requests
import os

files = {
    "ssm2024_suddivisione_contratti": "https://als-fattore2a.org/download/23755/",
    "als_abbandoni_area_medica": "https://als-fattore2a.org/download/23651/",
    "als_abbandoni_area_chirurgica": "https://als-fattore2a.org/download/23654/",
    "als_abbandoni_area_servizi": "https://als-fattore2a.org/download/23657/"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for name, url in files.items():
    print(f"Downloading {name}...")
    r = requests.get(url, headers=headers, allow_redirects=True, timeout=20)
    print(f"  Status: {r.status_code}, Length: {len(r.content)}, Content-Type: {r.headers.get('Content-Type')}")
    # Determine extension
    cd = r.headers.get('Content-Disposition', '')
    ext = ".bin"
    if '.pdf' in cd.lower() or 'pdf' in r.headers.get('Content-Type', '').lower():
        ext = ".pdf"
    elif '.xlsx' in cd.lower() or 'spreadsheet' in r.headers.get('Content-Type', '').lower():
        ext = ".xlsx"
    elif '.xls' in cd.lower():
        ext = ".xls"
    elif '.csv' in cd.lower():
        ext = ".csv"
    
    filename = f"data/raw/als_rinunce/{name}{ext}"
    with open(filename, "wb") as f:
        f.write(r.content)
    print(f"  Saved to {filename} (Content-Disposition: {cd})")
