import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0'}

# Search mur.gov.it for riparto SSM
for year in [2021, 2022, 2023, 2024]:
    url = f"https://www.mur.gov.it/it/ricerca?search_api_fulltext=riparto+SSM+{year}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip().replace('\n', ' ')
            if any(ext in href.lower() for ext in ['.xlsx', '.xls', '.pdf']) and ('riparto' in href.lower() or 'ssm' in href.lower() or 'allegato' in href.lower()):
                print(f"[{year}] {text[:60]} -> {href}")
    except Exception as e:
        print(f"Error {year}: {e}")
