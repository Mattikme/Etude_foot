"""
ingestion/fetch_injuries.py
--------------------------

Ce script récupère la liste des joueurs blessés pour les ligues qui ont un match
aujourd'hui. Il lit les fixtures du jour depuis ``fixtures_<league_id>_<date>.json``
et, pour chaque ligue ayant au moins un match aujourd'hui, appelle
l'endpoint ``/injuries`` avec le paramètre ``season`` approprié.

Les données sont stockées dans ``data/raw/injuries`` sous la forme
``injuries_<league_id>_<season>.json``.
"""

import os
import json
import yaml
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

# Détermination de la saison actuelle
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
TODAY = datetime.now().strftime("%Y-%m-%d")

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    data = yaml.safe_load(f)
    leagues = data.get("leagues", data)
    if isinstance(leagues, dict):
        target_leagues = list(leagues.values())
    else:
        target_leagues = list(leagues)

# Répertoire de sortie
os.makedirs("data/raw/injuries", exist_ok=True)

# Déterminer les ligues avec match aujourd'hui
active_leagues: list[str] = []
for league_id in target_leagues:
    fixture_path = f"data/raw/fixtures_{league_id}_{TODAY}.json"
    if not os.path.exists(fixture_path):
        continue
    with open(fixture_path, "r") as f_in:
        fixtures = json.load(f_in).get("response", [])
    # Si au moins un match se déroule aujourd'hui, ajouter la ligue
    if any(match.get("fixture", {}).get("date", "").startswith(TODAY) for match in fixtures):
        active_leagues.append(str(league_id))

for league_id in active_leagues:
    params = {"league": league_id, "season": SEASON}
    try:
        response = get("/injuries", params=params)
        output_path = f"data/raw/injuries/injuries_{league_id}_{SEASON}.json"
        with open(output_path, "w") as f_out:
            json.dump(response, f_out, indent=2)
        print(f"✅ Données blessures enregistrées pour ligue {league_id}")
    except Exception as e:
        print(f"❌ Erreur pour ligue {league_id} : {e}")