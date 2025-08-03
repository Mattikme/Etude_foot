# ingestion/fetch_odds_api_football.py
# -----------------------------------------------------------------------------
# Récupère les cotes pré‑match via API‑Football (RapidAPI ou officielle) pour
# toutes les ligues définies, à la date du jour. Les cotes sont sauvegardées
# dans data/raw/api_football_odds/odds_<fixture_id>.json.
# -----------------------------------------------------------------------------

import os
import json
import yaml
import sys
import time
from datetime import datetime

# Permet d'importer utils.request_handler depuis un script autonome
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.request_handler import get

# Date du jour
today = datetime.now().strftime("%Y-%m-%d")

# Charger la liste des ligues (IDs numériques)
with open("config/target_league_ids.yaml") as f:
    cfg = yaml.safe_load(f)
    leagues = cfg.get("leagues", cfg)
    if isinstance(leagues, dict):
        target_leagues = [int(v) for v in leagues.values()]
    else:
        target_leagues = [int(x) for x in leagues]

# Dossier de sortie
os.makedirs("data/raw/api_football_odds", exist_ok=True)

for league_id in target_leagues:
    try:
        # Un seul appel par ligue pour récupérer toutes les cotes du jour
        odds_resp = get("/odds", params={"league": league_id, "date": today})
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des cotes pour la ligue {league_id} : {e}")
        # Petite pause pour éviter un dépassement de quota en cas d'erreur
        time.sleep(1)
        continue

    matches = odds_resp.get("response", [])
    if not matches:
        print(f"⚠️ Aucune cote disponible aujourd'hui pour la ligue {league_id}")
        # Pause entre les ligues pour ne pas saturer l'API
        time.sleep(1)
        continue

    saved = 0
    for match in matches:
        # Chaque élément de la liste correspond à un fixture avec ses cotes
        fixture_id = match.get("fixture", {}).get("id")
        if fixture_id is None:
            continue
        out_path = f"data/raw/api_football_odds/odds_{fixture_id}.json"
        with open(out_path, "w") as out_file:
            json.dump(match, out_file, indent=2)
        saved += 1

    print(f"✅ {saved} fichier(s) de cotes enregistré(s) pour la ligue {league_id}")
    # Attendre une seconde avant de passer à la ligue suivante pour respecter les limites API
    time.sleep(1)
 
