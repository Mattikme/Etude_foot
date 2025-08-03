# ingestion/fetch_events.py
# -----------------------------------------------------------------------------
# Ce script récupère les événements (buts, cartons, remplacements...) uniquement
# pour les matchs du jour via l'endpoint /fixtures/events.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

# Détection de la saison actuelle
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
TODAY = datetime.now().date().isoformat()  # Format 'YYYY-MM-DD'

# Chargement des ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Création du dossier de sortie
os.makedirs("data/raw/events", exist_ok=True)

# Parcourir chaque ligue
for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"

    if not os.path.exists(fixtures_path):
        print(f"⚠️ Fixture manquant pour ligue {league_id}, fichier ignoré.")
        continue

    with open(fixtures_path, "r") as f:
        fixtures = json.load(f)

    # Filtrer uniquement les matchs du jour
    fixture_ids = [
        match["fixture"]["id"]
        for match in fixtures["response"]
        if match["fixture"]["date"].startswith(TODAY)
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
