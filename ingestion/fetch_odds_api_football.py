
import os
import json
import time
from utils.request_handler import get

BOOKMAKER_ID = 8  # Bet365
SAVE_DIR = "data/raw"

def fetch_and_save_odds():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    # Charger tous les fichiers fixtures disponibles dans data/raw
    fixture_files = [f for f in os.listdir(SAVE_DIR) if f.startswith("fixtures_") and f.endswith(".json")]

    for file in fixture_files:
        file_path = os.path.join(SAVE_DIR, file)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print(f"❌ Format non valide dans {file}")
            continue

        for fixture in data:
            fixture_id = fixture.get("fixture", {}).get("id")
            if not fixture_id:
                continue

            try:
                # Temporisation pour éviter le 429
                time.sleep(1.2)

                response = get("/odds", {
                    "fixture": fixture_id,
                    "bookmaker": BOOKMAKER_ID
                })
                odds = response.get("response", [])
                if not odds:
                    print(f"⚠️ Aucune cote pour le match {fixture_id}")
                    continue

                odds_filename = f"odds_{fixture_id}.json"
                odds_path = os.path.join(SAVE_DIR, odds_filename)

                with open(odds_path, "w", encoding="utf-8") as out:
                    json.dump(odds, out, indent=2)

                print(f"✅ Cotes enregistrées pour match {fixture_id}")
            except Exception as e:
                print(f"❌ Erreur cotes fixture {fixture_id} : {e}")
