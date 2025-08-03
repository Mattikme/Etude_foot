"""
ingestion/fetch_odds_api_football.py
-----------------------------------

Ce script récupère les cotes pré‑match via l'API‑Football (RapidAPI) plutôt
que via Pinnacle. Pour chaque match du jour listé dans les fichiers
``fixtures_<league_id>_<date>.json`` produits par ``fetch_fixtures.py``, il
appelle l'endpoint ``/odds/fixture/{fixture_id}`` et enregistre la réponse
complète dans ``data/raw/api_football_odds``.

Selon vos besoins, vous devrez extraire les cotes pertinentes (1X2, bookmakers
spécifiques) dans le script de mappage des cotes (preprocessing/match_odds_mapper.py).
"""

import os
import json
import yaml
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

TODAY = datetime.now().strftime("%Y-%m-%d")

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    data = yaml.safe_load(f)
    leagues = data.get("leagues", data)
    if isinstance(leagues, dict):
        target_leagues = list(leagues.values())
    else:
        target_leagues = list(leagues)

# Dossier de sortie
os.makedirs("data/raw/api_football_odds", exist_ok=True)

for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{TODAY}.json"
    if not os.path.exists(fixtures_path):
        continue
    with open(fixtures_path, "r") as f_in:
        fixtures = json.load(f_in).get("response", [])
    for match in fixtures:
        fixture = match.get("fixture", {})
        fixture_id = fixture.get("id")
        fixture_date = fixture.get("date", "")
        if not fixture_id or not fixture_date.startswith(TODAY):
            continue
        try:
            # Endpoint « odds/fixture/{fixture_id} » pour les cotes pré‑match
            endpoint = f"/odds/fixture/{fixture_id}"
            odds_resp = get(endpoint)
            out_path = f"data/raw/api_football_odds/odds_{fixture_id}.json"
            with open(out_path, "w") as f_out:
                json.dump(odds_resp, f_out, indent=2)
            print(f"✅ Cotes API‑Football enregistrées pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des cotes pour {fixture_id} : {e}")