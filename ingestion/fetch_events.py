# ingestion/fetch_events.py
# -----------------------------------------------------------------------------
# Ce script récupère les événements (buts, cartons, remplacements...) de chaque match
# via l'endpoint /fixtures/events. Il peut servir à enrichir les analyses in-play
# ou créer des métriques de pression/intensité du jeu.
# -----------------------------------------------------------------------------

import os
import json
from utils.request_handler import get

LEAGUE_ID = 39
SEASON = 2022

# Charger les fixtures existants
fixtures_path = f"data/raw/fixtures_{LEAGUE_ID}_{SEASON}.json"
with open(fixtures_path, "r") as f:
    fixtures = json.load(f)

fixture_ids = [match["fixture"]["id"] for match in fixtures["response"]]

# Dossier de sortie
os.makedirs("data/raw/events", exist_ok=True)

for fixture_id in fixture_ids:
    events = get("/fixtures/events", params={"fixture": fixture_id})
    output_path = f"data/raw/events/events_{fixture_id}.json"
    with open(output_path, "w") as f:
        json.dump(events, f, indent=2)
    print(f"✅ Événements sauvegardés pour match {fixture_id}")
