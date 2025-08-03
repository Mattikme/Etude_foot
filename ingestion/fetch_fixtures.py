# ingestion/fetch_fixtures.py
# -----------------------------------------------------------------------------
# Récupère toutes les rencontres du jour pour les ligues cibles.
# Ce script appelle l'endpoint `/fixtures` avec le paramètre `date=YYYY-MM-DD`
# afin de récupérer l'ensemble des matchs programmés aujourd'hui, au lieu de
# seulement le prochain match de chaque ligue.  Les résultats sont enregistrés
# dans `data/raw/fixtures_<league_id>_<date>.json`.
# -----------------------------------------------------------------------------

import os
import json
import yaml
import time
from datetime import datetime
import sys

# Ajouter la racine du projet au sys.path pour trouver utils.request_handler
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

TIMEZONE = "Europe/Paris"

# Charger la liste des ligues cibles
with open("config/target_league_ids.yaml") as f:
    data = yaml.safe_load(f)
    # Le fichier peut contenir une liste ou un dictionnaire id→nom
    leagues = data.get("leagues", data)
    if isinstance(leagues, dict):
        target_leagues = list(leagues.values())
    else:
        target_leagues = list(leagues)

# Créer le dossier de sortie
os.makedirs("data/raw", exist_ok=True)

# Date du jour au format ISO (YYYY-MM-DD)
today = datetime.now().strftime("%Y-%m-%d")

for league_id in target_leagues:
    params = {
        "league": league_id,
        "date": today,
        "timezone": TIMEZONE
    }
    success = False
    resp: dict | None = None
    for attempt in range(3):
        try:
            resp = get("/fixtures", params=params)
            # L'API renvoie un champ "get" indiquant l'endpoint appelé
            if isinstance(resp, dict) and resp.get("get") == "fixtures":
                success = True
                break
        except Exception as e:
            print(f"❌ Ligue {league_id} erreur (tentative {attempt+1}) : {e}")
        time.sleep(5)

    if not success or resp is None:
        print(f"⚠️ Échec après retries – ligue {league_id}")
        continue

    fixtures = resp.get("response", [])
    if not fixtures:
        print(f"⚠️ Aucun match programmé aujourd'hui pour la ligue {league_id}")
        continue

    out = f"data/raw/fixtures_{league_id}_{today}.json"
    with open(out, "w") as f_out:
        json.dump(resp, f_out, indent=2)
    print(f"✅ Ligue {league_id} – {len(fixtures)} match(s) sauvegardé(s) dans {out}")
