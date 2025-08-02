# ingestion/merge_dataset.py
# -----------------------------------------------------------------------------
# Ce script fusionne les données brutes (fixtures, stats, lineups, etc.)
# uniquement pour les matchs du jour, en un DataFrame exploitable pour le modèle.
# -----------------------------------------------------------------------------

import os
import json
import yaml
import pandas as pd
from datetime import datetime

# Détection de la saison et du jour actuel
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
TODAY = datetime.now().date()

# Ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

matches = []

for league_id in target_leagues:
    fixture_file = f"data/raw/fixtures_{league_id}_{SEASON}.json"
    if not os.path.exists(fixture_file):
        print(f"⚠️ Fixture manquant pour ligue {league_id}, ignoré.")
        continue

    with open(fixture_file, "r") as f:
        raw_fixtures = json.load(f)["response"]

    for match in raw_fixtures:
        date_match = datetime.fromisoformat(match["fixture"]["date"]).date()
        if date_match != TODAY:
            continue

        fixture_id = match["fixture"]["id"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        goals_home = match["goals"]["home"]
        goals_away = match["goals"]["away"]
        status = match["fixture"]["status"]["short"]
        matches.append({
            "fixture_id": fixture_id,
            "league_id": league_id,
            "date": date_match.isoformat(),
            "home": home,
            "away": away,
            "goals_home": goals_home,
            "goals_away": goals_away,
            "status": status
        })

# Convertir en DataFrame
matches_df = pd.DataFrame(matches)

# Créer dossier et sauvegarder
os.makedirs("data/processed", exist_ok=True)
matches_df.to_csv("data/processed/base_matches.csv", index=False)

print("✅ Base fusionnée pour les matchs du jour : data/processed/base_matches.csv")
