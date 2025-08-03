import requests
import yaml
from retry import retry

"""
Ce module centralise l'envoi des requêtes API‑Football.  Il gère à la fois les
clés de l'API officielle (`x-apisports-key`) et celles de RapidAPI (`x-rapidapi-key`).
Le fichier `config/api_keys.yaml` peut contenir :

api_football:
  key: "VOTRE_CLE_OFFICIELLE"
  host: "v3.football.api-sports.io"

rapidapi:
  key: "VOTRE_CLE_RAPIDAPI"
  host: "api-football-v1.p.rapidapi.com"

Si les deux sections sont présentes, la clé officielle est utilisée par défaut.
"""

def _load_keys() -> dict:
    """Charge et retourne le dictionnaire des clés depuis le fichier YAML."""
    with open("config/api_keys.yaml", "r") as f:
        return yaml.safe_load(f) or {}

def _build_headers_and_base() -> tuple[str, dict]:
    """
    Génère l'URL de base et les en‑têtes HTTP en fonction de la configuration.
    :return: tuple (base_url, headers)
    :raises ValueError: si aucune configuration valide n'est trouvée
    """
    keys = _load_keys()
    # Priorité à l'API officielle si disponible
    api_conf = keys.get("api_football", {})
    if api_conf.get("key") and api_conf.get("host"):
        key = api_conf["key"]
        host = api_conf["host"]
        headers = {"x-apisports-key": key}
        # l'hôte de l'API officielle inclut déjà '/v3'
        return f"https://{host}", headers

    # Sinon, utiliser RapidAPI si disponible
    rapid_conf = keys.get("rapidapi", {})
    if rapid_conf.get("key") and rapid_conf.get("host"):
        key = rapid_conf["key"]
        host = rapid_conf["host"]
        headers = {
            "x-rapidapi-key": key,
            "x-rapidapi-host": host,
        }
        # ajouter '/v3' pour les endpoints RapidAPI
        return f"https://{host}/v3", headers

    raise ValueError(
        "Aucune clé API valide n'est définie dans config/api_keys.yaml."
    )

@retry(tries=3, delay=2)
def get(endpoint: str, params: dict | None = None) -> dict:
    """
    Envoie une requête GET à l'API‑Football ou à RapidAPI selon la configuration.
    Réessaie automatiquement en cas d'erreur temporaire.
    :param endpoint: chemin de l'API (ex. '/fixtures')
    :param params: dictionnaire de paramètres (league, date, etc.)
    :return: la réponse JSON convertie en dict
    """
    base_url, headers = _build_headers_and_base()
    url = f"{base_url}{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
 
