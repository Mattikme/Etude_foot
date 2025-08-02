# ingestion/fetch_fixtures.py
# -----------------------------------------------------------------------------
# Ce script récupère uniquement les matchs du jour pour toutes les ligues ciblées
# en utilisant le paramètre "date" de l'API-Football, pour minimiser l’usage des quotas.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

# Date du jour au format YYYY-MM-DD
TODAY = datetime.now().strftime("%Y-%m-%d")

# Charger les IDs de ligue depuis le fichier YAML
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Créer le dossier de sortie
os.makedirs("data/raw", exist_ok=True)

# Récupérer uniquement les matchs du jour pour chaque ligue
for league_id in target_leagues:
    try:
        params = {
            "league": league_id,
            "date": TODAY
        }
        response = get("/fixtures", params=params)
        output_path = f"data/raw/fixtures_{league_id}_{TODAY}.json"
        with open(output_path, "w") as f_out:
            json.dump(response, f_out, indent=2)
        print(f"✅ Matchs du {TODAY} sauvegardés pour ligue {league_id}")
    except Exception as e:
        print(f"❌ Erreur pour ligue {league_id} : {e}")
