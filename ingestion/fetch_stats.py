# ingestion/fetch_stats.py
# -----------------------------------------------------------------------------
# Ce script utilise les fichiers de fixtures pour extraire les statistiques
# détaillées de chaque match via l'endpoint /fixtures/statistics.
# Fonctionne sur toutes les ligues définies dans target_league_ids.yaml
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

# Déterminer la saison automatiquement
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Répertoire de sortie
os.makedirs("data/raw/stats", exist_ok=True)

# Parcourir les fixtures pour chaque ligue
for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"
    
    if not os.path.exists(fixtures_path):
        print(f"⚠️ Fixtures manquants pour ligue {league_id}, ignoré.")
        continue

    with open(fixtures_path, "r") as f:
        fixtures = json.load(f)

    fixture_ids = [match["fixture"]["id"] for match in fixtures["response"]]

    for fixture_id in fixture_ids:
        try:
            stats = get("/fixtures/statistics", params={"fixture": fixture_id})
            output_path = f"data/raw/stats/statistics_{fixture_id}.json"
            with open(output_path, "w") as f_out:
                json.dump(stats, f_out, indent=2)
            print(f"✅ Statistiques enregistrées pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur pour fixture {fixture_id} : {e}")
