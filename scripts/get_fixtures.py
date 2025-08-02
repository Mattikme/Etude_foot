import requests
import yaml
from datetime import datetime
from pathlib import Path

# === Étape 1 : Charger les ligues autorisées ===
def load_target_leagues(yaml_path="config/target_league_ids.yaml"):
    with open(yaml_path, "r") as file:
        return set(yaml.safe_load(file)["leagues"].keys())

# === Étape 2 : Récupérer les fixtures du jour via API-Football ===
def get_fixtures_today(api_key):
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "date": datetime.today().strftime("%Y-%m-%d")
    }
    headers = {
        "x-rapidapi-host": "v3.football.api-sports.io",
        "x-rapidapi-key": api_key
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()["response"]

# === Étape 3 : Filtrer les fixtures selon les ligues autorisées ===
def filter_fixtures(fixtures, target_league_ids):
    return [
        f for f in fixtures if str(f["league"]["id"]) in target_league_ids
    ]

# === Étape 4 : Fonction principale ===
def main():
    api_key = "TA_CLE_API"  # 🔐 Remplace par ta vraie clé API

    # Charger les ligues à surveiller
    target_league_ids = load_target_leagues()

    # Récupérer les matchs du jour
    fixtures = get_fixtures_today(api_key)

    # Filtrer par ligues suivies
    filtered = filter_fixtures(fixtures, target_league_ids)

    # Affichage simple
    for match in filtered:
        league = match["league"]["name"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        print(f"{league}: {home} vs {away}")

if __name__ == "__main__":
    main()
