# ingestion/fetch_fixtures.py
# -----------------------------------------------------------------------------
# Récupère uniquement les matchs à venir ou du jour
# pour les ligues listées dans target_league_ids.yaml,
# et ignore les ligues sans fixtures programmés.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

TODAY = datetime.now().date().isoformat()

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Créer dossier de sortie
os.makedirs("data/raw", exist_ok=True)

# Pour chaque ligue, récupérer seulement si elle est active
for league_id in target_leagues:
    try:
        params = {"league": league_id, "date": TODAY}
        response = get("/fixtures", params=params)
    except Exception as e:
        print(f"❌ Erreur API pour ligue {league_id}: {e}")
        continue

    # Si aucune fixture, on ignore cette ligue
    fixtures = response.get("response", [])
    if not fixtures:
        print(f"⚠️ Pas de matchs programmés aujourd'hui pour ligue {league_id}, ignorée.")
        continue

    # Sinon on les sauvegarde
    output_path = f"data/raw/fixtures_{league_id}_{TODAY}.json"
    with open(output_path, "w") as f_out:
        json.dump(response, f_out, indent=2)
    print(f"✅ Matchs du jour pour ligue {league_id} sauvegardés ({len(fixtures)} fixtures)")
