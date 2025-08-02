# ingestion/fetch_pinnacle_odds.py
# --------------------------------------------------------------------------
# Ce script récupère les cotes Pinnacle pour les matchs à venir
# --------------------------------------------------------------------------

import pandas as pd
import datetime
import os
import yaml
from utils.request_handler import get

# 📅 Récupère la date du jour au format ISO
TODAY = datetime.datetime.now(datetime.UTC).date().isoformat()

# 📂 Charge les clés API Pinnacle depuis le fichier YAML
with open("config/pinnacle_keys.yaml", "r") as f:
    PINNACLE_KEYS = yaml.safe_load(f)

SPORT_ID = 29  # Football

def fetch_pinnacle_odds():
    all_odds = []

    for key in PINNACLE_KEYS:
        response = get(
            "https://api.pinnacle.com/v1/odds",
            headers={"Authorization": f"Basic {key}"},
            params={"sportId": SPORT_ID, "oddsFormat": "decimal"},
        )

        if not response or "leagues" not in response:
            print("❌ Aucune donnée renvoyée depuis Pinnacle")
            continue

        for league in response["leagues"]:
            for match in league.get("events", []):
                fixture_id = match.get("id")
                if not fixture_id:
                    continue

                for market in match.get("periods", []):
                    if market.get("number") != 0:
                        continue  # On prend uniquement les temps réglementaires

                    for outcome in market.get("moneyline", []):
                        ml = outcome.get("main_line")

                        if ml and all(k in ml for k in ["home", "draw", "away"]):
                            row = {
                                "fixture_id": fixture_id,
                                "timestamp": match.get("starts"),
                                "odds_home": ml["home"],
                                "odds_draw": ml["draw"],
                                "odds_away": ml["away"],
                            }
                            all_odds.append(row)
                        else:
                            print(f"❌ Cotes manquantes pour fixture {fixture_id}")

    return pd.DataFrame(all_odds)

# 💾 Sauvegarde les cotes
if __name__ == "__main__":
    df = fetch_pinnacle_odds()
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/pinnacle_odds.csv", index=False)
    print(f"✅ {len(df)} lignes de cotes sauvegardées.")
