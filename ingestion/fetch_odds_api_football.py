import os
import sys
import json
import time

# Correction pour les imports relatifs dans GitHub Actions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

BOOKMAKER_ID = 8  # Bet365
SAVE_DIR = "data/raw"

def fetch_and_save_odds():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    fixture_files = [f for f in os.listdir(SAVE_DIR) if f.startswith("fixtures_") and f.endswith(".json")]

    for file in fixture_files:
        file_path = os.path.join(SAVE_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "response" not in data or not isinstance(data["response"], list):
            print(f"❌ Format non valide dans {file}")
            continue

        for fixture in data["response"]:
            fixture_id = fixture.get("fixture", {}).get("id")
            league_id = fixture.get("league", {}).get("id")
            date = fixture.get("fixture", {}).get("date", "")[:10]
            if not fixture_id or not league_id or not date:
                continue

            try:
                time.sleep(1.2)

                response = get("/odds", {
                    "fixture": fixture_id,
                    "bookmaker": BOOKMAKER_ID
                })
                odds = response.get("response", [])
                if not odds:
                    print(f"⚠️ Aucune cote pour le match {fixture_id}")
                    continue

                odds_filename = f"odds_{league_id}_{date}.json"
                odds_path = os.path.join(SAVE_DIR, odds_filename)

                with open(odds_path, "w", encoding="utf-8") as out:
                    json.dump(response, out, indent=2)

                print(f"✅ Cotes enregistrées pour match {fixture_id} ({league_id})")
            except Exception as e:
                print(f"❌ Erreur cotes fixture {fixture_id} : {e}")

if __name__ == "__main__":
    fetch_and_save_odds() 
