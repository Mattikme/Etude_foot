# utils/request_handler.py
# -----------------------------------------------------------------------------
# Module utilitaire pour centraliser l'envoi des requêtes API vers API-Football
# Gère : headers dynamiques, timeout, erreurs, et options de log
# -----------------------------------------------------------------------------

import requests
import yaml
from retry import retry

# Chargement des clés API depuis le fichier YAML sécurisé
with open("config/api_keys.yaml", "r") as f:
    keys = yaml.safe_load(f)

API_KEY = keys["api_football"]["key"]
BASE_URL = f"https://{keys['api_football']['host']}"

HEADERS = {
    "x-apisports-key": API_KEY
}

@retry(tries=3, delay=2)
def get(endpoint: str, params: dict = None):
    """
    Fonction générique pour appeler un endpoint GET de l'API-Football.
    Réessaie automatiquement en cas d'erreur temporaire (rate limit, timeout).
    
    Args:
        endpoint (str): le chemin de l'API (ex: '/fixtures')
        params (dict): les paramètres de requête (ex: league, season...)

    Returns:
        dict: réponse JSON décodée
    """
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()
