# ingestion/fetch_lineups.py
# -----------------------------------------------------------------------------
# Ce script permet de récupérer les compositions d'équipe (lineups) de chaque match
# via l'endpoint /fixtures/lineups de l'API-Football et de les stocker localement.
# -----------------------------------------------------------------------------

import os
import json
from utils.request_handler import get

# Paramètres de la saison ciblée
LEAGUE_ID = 39
SEASON = 2022

# Charger les fixtures déjà récupérés
fixtures_path = f"data/raw/fixtures_{LEAGUE_ID}_{SEASON}.json"
with open(fixtures_path, "r") as f:
    fixtures = json.load(f)

# Extraire tous les IDs de match (fixtures)
fixture_ids = [match["fixture"]["id"] for match in fixtures["response"]]

# Répertoire de sortie
os.makedirs("data/raw/lineups", exist_ok=True)

# Récupérer et sauvegarder les compositions de chaque match
for fixture_id in fixture_ids:
    lineups = get("/fixtures/lineups", params={"fixture": fixture_id})
    output_path = f"data/raw/lineups/lineups_{fixture_id}.json"
    with open(output_path, "w") as f:
        json.dump(lineups, f, indent=2)
    print(f"✅ Lineup enregistré pour match {fixture_id}")
