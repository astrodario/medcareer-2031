import os
import requests
from bs4 import BeautifulSoup
import json

os.makedirs("data/raw/als_rinunce", exist_ok=True)

urls = [
    ("borse_perse", "https://als-fattore2a.org/borse-perse/"),
    ("statistica_ssm2025", "https://als-fattore2a.org/uncategorized/statistica-prima-assegnazione-ssm2025/"),
    ("suddivisione_contratti_ssm2024", "https://als-fattore2a.org/news/suddivisione-contratti-ssm2024-anticipazione/"),
    ("analisi_abbandoni_non_assegnazioni", "https://als-fattore2a.org/uncategorized/analisi-abbandoni-e-non-assegnazione-contratti-di-specializzazione/"),
    ("ssm2024_punto", "https://als-fattore2a.org/uncategorized/ssm-2024-facciamo-il-punto/"),
    ("day_after_ssm2024", "https://als-fattore2a.org/uncategorized/day-after-ssm2024-tutte-le-analisi-e-studi/")
]

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for slug, url in urls:
    print(f"Fetching {slug}...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # save raw html
            with open(f"data/raw/als_rinunce/{slug}.html", "w", encoding="utf-8") as f:
                f.write(r.text)
            
            # Check for tables
            tables = soup.find_all('table')
            print(f"  Saved {slug}.html - Found {len(tables)} tables")
            
            # Check for pdf or doc links
            for a in soup.find_all('a', href=True):
                href = a['href']
                if any(ext in href.lower() for ext in ['.pdf', '.xlsx', '.xls', '.csv']):
                    print(f"  Found document link in {slug}: {href}")
        else:
            print(f"  Error {slug}: status {r.status_code}")
    except Exception as e:
        print(f"  Failed {slug}: {e}")
