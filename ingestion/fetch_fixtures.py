# ingestion/fetch_fixtures.py
# ---------------------------------------------------------------------------
# Récupère toutes les rencontres du jour et les répartit par ligue.
# Les fichiers sont enregistrés dans data/raw/fixtures_<league_id>_<date>.json
# ---------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
import sys

# Ajouter la racine du projet au sys.path pour import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.request_handler import get

TIMEZONE = "Europe/Paris"
today = datetime.now().strftime("%Y-%m-%d")

# Charger les IDs des ligues cibles
with open("config/target_league_ids.yaml") as f:
    cfg = yaml.safe_load(f)
    leagues = cfg.get("leagues", cfg)
    if isinstance(leagues, dict):
        target_leagues = [int(v) for v in leagues.values()]
    else:
        target_leagues = [int(x) for x in leagues]

# Créer le dossier de sortie
os.makedirs("data/raw", exist_ok=True)

# 1. Appel global aux fixtures du jour
try:
    all_fixtures = get("/fixtures", params={"date": today, "timezone": TIMEZONE})
    fixtures_list = all_fixtures.get("response", [])
except Exception as e:
    print(f"❌ Erreur lors de la récupération des fixtures du jour : {e}")
    fixtures_list = []

# 2. Filtrer par ligue et sauvegarder
for league_id in target_leagues:
    matches = [f for f in fixtures_list if f.get("league", {}).get("id") == league_id]
    if not matches:
        print(f"⚠️ Aucun match programmé aujourd'hui pour la ligue {league_id}")
        continue

    # On reconstitue une réponse similaire à l'API pour garder le même format
    response = {
        "get": "fixtures",
        "parameters": {"league": league_id, "date": today, "timezone": TIMEZONE},
        "errors": [],
        "results": len(matches),
        "paging": {"current": 1, "total": 1},
        "response": matches,
    }
    out_path = f"data/raw/fixtures_{league_id}_{today}.json"
    with open(out_path, "w") as f_out:
        json.dump(response, f_out, indent=2)
    print(f"✅ {len(matches)} match(s) sauvegardé(s) pour la ligue {league_id} dans {out_path}")
 
