# ingestion/fetch_standings.py
# -----------------------------------------------------------------------------
# Ce script récupère le classement complet d'une ligue pour une saison donnée,
# pour toutes les ligues définies dans config/target_league_ids.yaml.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

# Détection de la saison en cours
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Répertoire de sortie
os.makedirs("data/raw/standings", exist_ok=True)

# Boucle sur chaque ligue pour appeler l'endpoint standings
for league_id in target_leagues:
    try:
        response = get("/standings", params={"league": league_id, "season": SEASON})
        output_path = f"data/raw/standings/standings_{league_id}_{SEASON}.json"
        with open(output_path, "w") as f_out:
            json.dump(response, f_out, indent=2)
        print(f"✅ Classement sauvegardé pour ligue {league_id} dans {output_path}")
    except Exception as e:
        print(f"❌ Erreur pour ligue {league_id} : {e}")
