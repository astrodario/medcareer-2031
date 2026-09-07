import zipfile
import os

zip_files = [
    ("data/raw/als_rinunce/als_abbandoni_area_medica.bin", "data/raw/als_rinunce/area_medica"),
    ("data/raw/als_rinunce/als_abbandoni_area_chirurgica.bin", "data/raw/als_rinunce/area_chirurgica"),
    ("data/raw/als_rinunce/als_abbandoni_area_servizi.bin", "data/raw/als_rinunce/area_servizi")
]

for src, dest in zip_files:
    os.makedirs(dest, exist_ok=True)
    try:
        with zipfile.ZipFile(src, 'r') as zip_ref:
            print(f"Extracting {src} into {dest} ({len(zip_ref.namelist())} files)...")
            zip_ref.extractall(dest)
            for name in zip_ref.namelist()[:10]:
                print(f"  - {name}")
    except Exception as e:
        print(f"Error extracting {src}: {e}")
