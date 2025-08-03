# tools/generate_allowed_leagues.py
# -----------------------------------------------------------------------------
# Ce script est désormais obsolète.  La liste des ligues autorisées est définie
# directement dans `config/target_league_ids.yaml`.  Cette version n'appelle
# plus l'API et se contente d'informer l'utilisateur.
# -----------------------------------------------------------------------------

def main() -> None:
    print(
        "ℹ️ Ce script est obsolète : utilisez le fichier config/target_league_ids.yaml "
        "pour gérer les ligues suivies.  Aucune action n'a été effectuée."
    )


if __name__ == "__main__":
    main() 
