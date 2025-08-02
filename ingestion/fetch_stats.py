# ingestion/fetch_stats.py
# -----------------------------------------------------------------------------
# Ce script utilise les fichiers de fixtures pour extraire les statistiques
# détaillées de chaque match via l'endpoint /fixtures/statistics de l'API-Football
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
os.makedirs("data/raw/stats", exist_ok=True)

# Récupérer et sauvegarder les stats de chaque match individuellement
for fixture_id in fixture_ids:
    stats = get("/fixtures/statistics", params={"fixture": fixture_id})
    output_path = f"data/raw/stats/statistics_{fixture_id}.json"
    with open(output_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"✅ Statistiques enregistrées pour match {fixture_id}")
