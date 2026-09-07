import os
import requests

os.makedirs("data/raw/mur_ssm", exist_ok=True)
url = "https://www.mur.gov.it/sites/default/files/2023-09/Allegato%20al%20DM%20n.1268-2023%20riparto%20SSM%2022-23_rettificato.xlsx"
headers = {'User-Agent': 'Mozilla/5.0'}

r = requests.get(url, headers=headers, timeout=20)
print("MUR Excel status:", r.status_code, "len:", len(r.content))
if r.status_code == 200:
    path = "data/raw/mur_ssm/riparto_SSM_22_23.xlsx"
    with open(path, "wb") as f:
        f.write(r.content)
    print("Saved to", path)
