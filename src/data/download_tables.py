import requests

headers = {'User-Agent': 'Mozilla/5.0'}

# 1. Download tabela scuole 2025
url1 = 'https://www.anaao.it/public/aaa_9617029_tabella_scuole2025.png'
r1 = requests.get(url1, headers=headers)
print("tabella_scuole2025 status:", r1.status_code, len(r1.content))
with open('data/raw/als_rinunce/tabella_scuole2025.png', 'wb') as f:
    f.write(r1.content)

# 2. Download day after ssm 2024 download
url2 = 'https://als-fattore2a.org/download/23378/'
r2 = requests.get(url2, headers=headers, allow_redirects=True)
print("day after 2024 status:", r2.status_code, len(r2.content), r2.headers.get('Content-Disposition'))
with open('data/raw/als_rinunce/day_after_2024_attachment.bin', 'wb') as f:
    f.write(r2.content)
