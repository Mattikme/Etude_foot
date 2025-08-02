# ingestion/fetch_events.py
# -----------------------------------------------------------------------------
# Ce script récupère les événements (buts, cartons, remplacements...) de chaque match
# via l'endpoint /fixtures/events. Il couvre toutes les ligues listées dans
# config/target_league_ids.yaml pour la saison en cours.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

# Détection automatique de la saison (ex. 2023 pour la saison 2023-2024)
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Chargement des ligues cibles depuis le fichier YAML
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Création du dossier de sortie
os.makedirs("data/raw/events", exist_ok=True)

# Récupération des événements pour chaque fixture de chaque ligue
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
            events = get("/fixtures/events", params={"fixture": fixture_id})
            output_path = f"data/raw/events/events_{fixture_id}.json"
            with open(output_path, "w") as f_out:
                json.dump(events, f_out, indent=2)
            print(f"✅ Événements sauvegardés pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur pour fixture {fixture_id} : {e}")
