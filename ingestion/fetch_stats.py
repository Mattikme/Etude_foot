"""
ingestion/fetch_stats.py
-------------------------

Ce script récupère les statistiques détaillées pour les rencontres du jour.
Il parcourt les fichiers produits par ``ingestion/fetch_fixtures.py`` (nommés
``fixtures_<league_id>_<date>.json``) et, pour chaque match programmé aujourd'hui,
appelle l'endpoint ``/fixtures/statistics`` de l'API‑Football via le module
``utils.request_handler``.

Les statistiques de chaque match sont sauvegardées dans ``data/raw/stats`` sous
le nom ``statistics_<fixture_id>.json``.
"""

import os
import json
import yaml
from datetime import datetime

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

# La saison courante reste utilisée pour l'appel API (certaines statistiques
# nécessitent le paramètre ``season``).
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
TODAY = datetime.now().strftime("%Y-%m-%d")

# Charger la liste des ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    data = yaml.safe_load(f)
    leagues = data.get("leagues", data)
    if isinstance(leagues, dict):
        target_leagues = list(leagues.values())
    else:
        target_leagues = list(leagues)

# Créer le dossier de sortie
os.makedirs("data/raw/stats", exist_ok=True)

for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{TODAY}.json"
    if not os.path.exists(fixtures_path):
        print(f"⚠️ Fixtures manquants pour ligue {league_id}, ignoré.")
        continue

    with open(fixtures_path, "r") as f_in:
        fixtures = json.load(f_in).get("response", [])

    for match in fixtures:
        fixture = match.get("fixture", {})
        fixture_id = fixture.get("id")
        date_str = fixture.get("date")
        # Vérifier que le match se déroule aujourd'hui
        if not fixture_id or not date_str or not date_str.startswith(TODAY):
            continue
        try:
            stats = get("/fixtures/statistics", params={"fixture": fixture_id})
            output_path = f"data/raw/stats/statistics_{fixture_id}.json"
            with open(output_path, "w") as f_out:
                json.dump(stats, f_out, indent=2)
            print(f"✅ Statistiques enregistrées pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur pour fixture {fixture_id} : {e}")