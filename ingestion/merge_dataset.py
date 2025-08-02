# ingestion/merge_dataset.py
# -----------------------------------------------------------------------------
# Fusionne tous les fichiers JSON de fixtures actifs pour créer une base unique
# -----------------------------------------------------------------------------

import os
import json
import pandas as pd
from glob import glob
from datetime import datetime

DATA_DIR = "data/raw"
OUTPUT_FILE = "data/processed/base_matches.csv"
os.makedirs("data/processed", exist_ok=True)

fixtures = []

# Rechercher tous les fichiers JSON des fixtures
for filepath in glob(os.path.join(DATA_DIR, "fixtures_*.json")):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            matches = data.get("response", [])
            if matches:
                fixtures.extend(matches)
            else:
                print(f"⚠️ Fichier vide ou sans match : {filepath}")
    except Exception as e:
        print(f"❌ Erreur lecture fichier {filepath} : {e}")

# Si aucun match trouvé, on évite de créer un CSV vide
if not fixtures:
    print("❌ Aucun match à fusionner, fichier de sortie non généré.")
else:
    # Normalisation et création du DataFrame
    df = pd.json_normalize(fixtures)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Base fusionnée pour les matchs du jour : {OUTPUT_FILE}")
