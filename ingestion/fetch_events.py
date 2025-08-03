"""
ingestion/fetch_events.py
-------------------------

Ce script récupère les événements (buts, cartons, remplacements, etc.) pour les
matchs du jour. Il lit les fixtures du jour depuis ``fixtures_<league_id>_<date>.json``
et appelle l'endpoint ``/fixtures/events`` pour chaque fixture.

Les résultats sont stockés dans ``data/raw/events`` sous la forme
``events_<fixture_id>.json``.
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

os.makedirs("data/raw/events", exist_ok=True)

for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{TODAY}.json"
    if not os.path.exists(fixtures_path):
        print(f"⚠️ Fixture manquant pour ligue {league_id}, fichier ignoré.")
        continue
    with open(fixtures_path, "r") as f_in:
        fixtures = json.load(f_in).get("response", [])
    # Récupérer les fixtures du jour
    fixture_ids = [
        match.get("fixture", {}).get("id")
        for match in fixtures
        if match.get("fixture", {}).get("date", "").startswith(TODAY)
    ]
    for fixture_id in fixture_ids:
        try:
            events = get("/fixtures/events", params={"fixture": fixture_id})
            output_path = f"data/raw/events/events_{fixture_id}.json"
            with open(output_path, "w") as f_out:
                json.dump(events, f_out, indent=2)
            print(f"✅ Événements sauvegardés pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur pour fixture {fixture_id} : {e}")