import os
import requests
import zipfile

os.makedirs("data/raw/istat", exist_ok=True)

istat_files = [
    ("Previsioni-Popolazione_per_eta-Regioni.zip", "https://demo.istat.it/data/previsioni/Previsioni-Popolazione_per_eta-Regioni.zip"),
    ("Indicatori-Regioni.zip", "https://demo.istat.it/data/previsioni/Indicatori-Regioni.zip"),
    ("Componenti_del_bilancio_demografico-Regioni.zip", "https://demo.istat.it/data/previsioni/Componenti_del_bilancio_demografico-Regioni.zip")
]

headers = {'User-Agent': 'Mozilla/5.0'}

for name, url in istat_files:
    path = os.path.join("data/raw/istat", name)
    print(f"Downloading {name} from {url}...")
    r = requests.get(url, headers=headers, timeout=20)
    print(f"  Status: {r.status_code}, Length: {len(r.content)}")
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        # Extract zip
        extract_to = os.path.join("data/raw/istat", name.replace(".zip", ""))
        os.makedirs(extract_to, exist_ok=True)
        with zipfile.ZipFile(path, 'r') as z:
            z.extractall(extract_to)
            print(f"  Extracted into {extract_to}: {z.namelist()[:5]}")
