# ingestion/fetch_standings.py
# ---------------------------------------------------------------------------
# Récupère les classements (standings) pour chaque ligue de la saison en cours.
# Les fichiers sont enregistrés sous la forme standings_<league_id>_<saison>.json
# dans data/raw/standings/.
# ---------------------------------------------------------------------------

import os
import json
import yaml
import time
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

# Saison courante (format AAAA), ajustez si nécessaire
SEASON = datetime.now().year

# Charger la liste des ligues (IDs)
with open("config/target_league_ids.yaml") as f:
    data = yaml.safe_load(f)
    leagues = data.get("leagues", data)
    # Si dictionnaire "nom: id", prendre les valeurs; sinon, prendre la liste
    if isinstance(leagues, dict):
        target_leagues = [int(v) for v in leagues.values()]
    else:
        target_leagues = [int(x) for x in leagues]

os.makedirs("data/raw/standings", exist_ok=True)

for league_id in target_leagues:
    params = {
        "league": league_id,
        "season": SEASON
    }
    try:
        resp = get("/standings", params=params)
        out_file = f"data/raw/standings/standings_{league_id}_{SEASON}.json"
        with open(out_file, "w") as f_out:
            json.dump(resp, f_out, indent=2)
        print(f"✅ Classement sauvegardé pour ligue {league_id} dans {out_file}")
    except Exception as e:
        print(f"❌ Erreur pour ligue {league_id} : {e}")
        # petite pause avant de poursuivre (optionnel)
        time.sleep(2)
