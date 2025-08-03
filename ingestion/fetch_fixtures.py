# ingestion/fetch_fixtures.py
import sys
sys.path.append(".")

import os, json, yaml, time
from datetime import datetime
from utils.request_handler import get

TODAY = datetime.now().date().isoformat()
TIMEZONE = "Europe/Paris"

with open("config/target_league_ids.yaml") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

os.makedirs("data/raw", exist_ok=True)

for league_id in target_leagues:
    params = {
        "league": league_id,
        "date": TODAY,
        "status": "NS",  # uniquement les matchs à venir
        "timezone": TIMEZONE
    }
    success = False
    for attempt in range(3):
        try:
            resp = get("/fixtures", params=params)
            if resp.get("get") == "fixtures":
                success = True
                break
        except Exception as e:
            print(f"❌ Ligue {league_id} erreur (tentative {attempt+1}) : {e}")
        time.sleep(5)

    if not success:
        print(f"⚠️ Échec après retries – ligue {league_id}")
        continue

    fixtures = resp.get("response", [])
    if not fixtures:
        print(f"⚠️ Aucune rencontre NS aujourd’hui pour ligue {league_id}")
        continue

    out = f"data/raw/fixtures_{league_id}_{TODAY}.json"
    with open(out, "w") as f:
        json.dump(resp, f, indent=2)
    print(f"✅ Ligues {league_id} – {len(fixtures)} fixture(s) sauvegardée(s)")
 
