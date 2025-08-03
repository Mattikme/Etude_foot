import os
import json
import pandas as pd
from glob import glob

DATA_DIR = "data/raw"
OUTPUT_FILE = "data/processed/base_matches.csv"
os.makedirs("data/processed", exist_ok=True)

fixtures = []

# Rechercher tous les fichiers JSON valides
json_files = glob(os.path.join(DATA_DIR, "fixtures_*.json"))
if not json_files:
    print("❌ Aucun fichier de fixtures trouvé dans data/raw/")
else:
    for filepath in json_files:
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                matches = data.get("response", [])
                if matches:
                    fixtures.extend(matches)
                    print(f"✅ {len(matches)} matchs extraits de {os.path.basename(filepath)}")
                else:
                    print(f"⚠️ Aucun match (status NS ?) dans {filepath}")
        except Exception as e:
            print(f"❌ Erreur lecture fichier {filepath} : {e}")

# Génération CSV si data trouvée
if not fixtures:
    print("❌ Aucun match à fusionner, fichier de sortie non généré.")
else:
    df = pd.json_normalize(fixtures)
    
    if df.empty or df.shape[1] == 0:
        print("❌ Le DataFrame est vide ou sans colonnes valides.")
    else:
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Base fusionnée pour les matchs du jour : {OUTPUT_FILE}")
