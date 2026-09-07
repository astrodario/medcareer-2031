import os
import requests

os.makedirs("data/raw/anaao_studies", exist_ok=True)

studies = {
    "anaao_pletora_2024.pdf": "http://www.anaao.it/public/aaa_8255733_studiocompletopletora_4marzo2024.pdf",
    "anaao_dimissioni_2022.pdf": "http://www.anaao.it/public/aaa_8152960_studiodimissioni_21aprile2022.pdf",
    "anaao_carenza_regioni_2019.pdf": "http://www.anaao.it/public/aaa_6280813_studioanaao_carenzaregioni_20marzo2019.pdf",
    "anaao_fabbisogni_2018_2025.pdf": "http://www.anaao.it/public/aaa_4025365_fabbisogni_2018-2025_versione_05_01_2019.pdf"
}

headers = {'User-Agent': 'Mozilla/5.0'}

for name, url in studies.items():
    dest = os.path.join("data/raw/anaao_studies", name)
    if not os.path.exists(dest):
        print(f"Downloading {name} from {url}...")
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            with open(dest, 'wb') as f:
                f.write(r.content)
            print(f"Saved {name} ({len(r.content)} bytes)")
        else:
            print(f"Failed {name}: status {r.status_code}")
    else:
        print(f"Already exists: {name}")
