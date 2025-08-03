# scripts/get_fixtures.py
# -----------------------------------------------------------------------------
# Exemple de récupération des rencontres du jour via API‑Football
# Ce script est conservé à titre d'exemple mais il n'est plus utilisé par le
# pipeline principal.  Il lit la liste des ligues cibles dans
# `config/target_league_ids.yaml` et appelle l'endpoint `/fixtures` via
# `utils.request_handler.get`, qui gère l'authentification et les retries.
# -----------------------------------------------------------------------------

from datetime import datetime
from pathlib import Path
import yaml
import sys
sys.path.append(".")
from utils.request_handler import get  # type: ignore


def load_target_league_ids(yaml_path: str = "config/target_league_ids.yaml") -> set[str]:
    """Charge les identifiants de ligue cibles depuis le YAML."""
    with open(yaml_path, "r") as file:
        data = yaml.safe_load(file)
        # Le fichier peut stocker une liste directement ou un mapping id→nom
        leagues = data.get("leagues", data)
        if isinstance(leagues, dict):
            return set(str(key) for key in leagues.keys())
        return set(str(item) for item in leagues)


def get_fixtures_today(date: str) -> list[dict]:
    """Récupère les fixtures du jour via l'API-Football."""
    response = get(
        "/fixtures",
        params={"date": date},
    )
    return response.get("response", []) if isinstance(response, dict) else []


def filter_fixtures(fixtures: list[dict], target_league_ids: set[str]) -> list[dict]:
    """Filtre les rencontres pour ne garder que celles des ligues cibles."""
    return [
        f for f in fixtures if str(f["league"]["id"]) in target_league_ids
    ]


def main() -> None:
    # Date du jour au format YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    target_leagues = load_target_league_ids()
    fixtures = get_fixtures_today(today)
    filtered = filter_fixtures(fixtures, target_leagues)
    # Affichage simple
    for match in filtered:
        league = match["league"]["name"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        print(f"{league}: {home} vs {away}")


if __name__ == "__main__":
    main()
def filter_fixtures(fixtures: list[dict], target_league_ids: set[str]) -> list[dict]:
    """Filtre les rencontres pour ne garder que celles des ligues cibles."""
    return [
        f for f in fixtures if str(f["league"]["id"]) in target_league_ids
    ]


def main() -> None:
    # Date du jour au format YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    target_leagues = load_target_league_ids()
    fixtures = get_fixtures_today(today)
    filtered = filter_fixtures(fixtures, target_leagues)
    # Affichage simple
    for match in filtered:
        league = match["league"]["name"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        print(f"{league}: {home} vs {away}")


if __name__ == "__main__":
    main() 
