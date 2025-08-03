# ingestion/fetch_injuries.py
# -----------------------------------------------------------------------------
# Ce script récupère la liste des joueurs blessés uniquement pour les ligues
# ayant des matchs aujourd’hui (détecté via fixtures), pour la saison actuelle.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

# Détecter la saison actuelle
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
TODAY = datetime.now().date().isoformat()

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    all_leagues = yaml.safe_load(f)["leagues"]

# Créer le dossier de sortie
os.makedirs("data/raw/injuries", exist_ok=True)

# Déterminer les ligues avec matchs aujourd’hui
active_leagues = []
for league_id in all_leagues:
    fixture_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"
    if not os.path.exists(fixture_path):
        continue

    with open(fixture_path, "r") as f:
        fixtures = json.load(f)["response"]

    if any(match["fixture"]["date"].startswith(TODAY) for match in fixtures):
        active_leagues.append(league_id)

# Appels API uniquement pour les ligues actives
for league_id in active_leagues:
    params = {
        "league": league_id,
        "season": SEASON
    }
    try:
        response = get("/injuries", params=params)
        output_path = f"data/raw/injuries/injuries_{league_id}_{SEASON}.json"
        with open(output_path, "w") as f_out:
            json.dump(response, f_out, indent=2)
        print(f"✅ Données blessures enregistrées pour ligue {league_id}")
    except Exception as e:
        print(f"❌ Erreur pour ligue {league_id} : {e}")
