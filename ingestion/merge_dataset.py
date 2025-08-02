# ingestion/merge_dataset.py
# -----------------------------------------------------------------------------
# Ce script fusionne les données brutes (fixtures, stats, lineups, etc.)
# en un seul DataFrame exploitable pour l'entraînement du modèle LSTM.
# Il extrait des features de base comme : résultats, stats match, absents, etc.
# -----------------------------------------------------------------------------

import os
import json
import yaml
import pandas as pd
from datetime import datetime

# Saison automatiquement déterminée
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Chargement des ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

matches = []

for league_id in target_leagues:
    fixture_file = f"data/raw/fixtures_{league_id}_{SEASON}.json"
    if not os.path.exists(fixture_file):
        print(f"⚠️ Fichier manquant pour ligue {league_id}")
        continue

    with open(fixture_file, "r") as f:
        raw_fixtures = json.load(f)["response"]

    for match in raw_fixtures:
        fixture_id = match["fixture"]["id"]
        date = match["fixture"]["date"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        goals_home = match["goals"]["home"]
        goals_away = match["goals"]["away"]
        status = match["fixture"]["status"]["short"]
        matches.append({
            "fixture_id": fixture_id,
            "league_id": league_id,
            "date": date,
            "home": home,
            "away": away,
            "goals_home": goals_home,
            "goals_away": goals_away,
            "status": status
        })

# Conversion en DataFrame global
matches_df = pd.DataFrame(matches)

# Dossier de sortie
os.makedirs("data/processed", exist_ok=True)

# Sauvegarde CSV
matches_df.to_csv("data/processed/base_matches.csv", index=False)

print("✅ Base de données fusionnée : data/processed/base_matches.csv")
