"""
ingestion/fetch_lineups.py
--------------------------

Ce script récupère les compositions d'équipe (lineups) pour les matches du jour.
Il lit les fichiers ``fixtures_<league_id>_<date>.json`` générés par
``ingestion/fetch_fixtures.py``, filtre les matches du jour et appelle
l'endpoint ``/fixtures/lineups`` pour chaque fixture.

Les résultats sont stockés dans ``data/raw/lineups`` sous la forme
``lineups_<fixture_id>.json``.
"""

import os
import json
import yaml
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

TODAY = datetime.now().strftime("%Y-%m-%d")

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    data = yaml.safe_load(f)
    leagues = data.get("leagues", data)
    if isinstance(leagues, dict):
        target_leagues = list(leagues.values())
    else:
        target_leagues = list(leagues)

# Dossier de sortie
os.makedirs("data/raw/lineups", exist_ok=True)

for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{TODAY}.json"
    if not os.path.exists(fixtures_path):
        continue
    with open(fixtures_path, "r") as f_in:
        fixtures = json.load(f_in).get("response", [])
    for match in fixtures:
        fixture = match.get("fixture", {})
        fixture_id = fixture.get("id")
        fixture_date = fixture.get("date")
        if fixture_id and fixture_date and fixture_date.startswith(TODAY):
            try:
                lineups = get("/fixtures/lineups", params={"fixture": fixture_id})
                output_path = f"data/raw/lineups/lineups_{fixture_id}.json"
                with open(output_path, "w") as f_out:
                    json.dump(lineups, f_out, indent=2)
                print(f"✅ Composition enregistrée pour match {fixture_id}")
            except Exception as e:
                print(f"❌ Erreur pour match {fixture_id} : {e}")