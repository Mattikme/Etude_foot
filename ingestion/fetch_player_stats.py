# ingestion/fetch_player_stats.py
# -----------------------------------------------------------------------------
# Ce script permet de récupérer les statistiques individuelles des joueurs
# pour chaque match via l'endpoint /fixtures/players, pour toutes les ligues
# définies dans config/target_league_ids.yaml.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

# Détection automatique de la saison actuelle
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Dossier de sortie
os.makedirs("data/raw/player_stats", exist_ok=True)

# Boucle sur les ligues
for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"

    if not os.path.exists(fixtures_path):
        print(f"⚠️ Fixture manquant pour ligue {league_id}, fichier ignoré.")
        continue

    with open(fixtures_path, "r") as f:
        fixtures = json.load(f)

    fixture_ids = [match["fixture"]["id"] for match in fixtures["response"]]

    for fixture_id in fixture_ids:
        try:
            players = get("/fixtures/players", params={"fixture": fixture_id})
            output_path = f"data/raw/player_stats/player_stats_{fixture_id}.json"
            with open(output_path, "w") as f_out:
                json.dump(players, f_out, indent=2)
            print(f"✅ Statistiques joueurs enregistrées pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur pour fixture {fixture_id} : {e}")
