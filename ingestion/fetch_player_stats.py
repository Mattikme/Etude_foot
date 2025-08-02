# ingestion/fetch_player_stats.py
# -----------------------------------------------------------------------------
# Ce script permet de récupérer les statistiques individuelles des joueurs
# pour chaque match via l'endpoint /fixtures/players. Ces données sont
# utiles pour construire des features avancées ou analyser les performances.
# -----------------------------------------------------------------------------

import os
import json
from utils.request_handler import get

LEAGUE_ID = 39
SEASON = 2022

fixtures_path = f"data/raw/fixtures_{LEAGUE_ID}_{SEASON}.json"
with open(fixtures_path, "r") as f:
    fixtures = json.load(f)

fixture_ids = [match["fixture"]["id"] for match in fixtures["response"]]

os.makedirs("data/raw/player_stats", exist_ok=True)

for fixture_id in fixture_ids:
    players = get("/fixtures/players", params={"fixture": fixture_id})
    output_path = f"data/raw/player_stats/player_stats_{fixture_id}.json"
    with open(output_path, "w") as f:
        json.dump(players, f, indent=2)
    print(f"✅ Statistiques joueurs enregistrées pour match {fixture_id}")
