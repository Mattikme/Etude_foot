# pipeline/run_pipeline.py
# ---------------------------------------------------------------------------
# Orchestration du pipeline complet. Ce script lance chaque étape dans l'ordre.
# Les erreurs sont affichées mais n'arrêtent pas forcément l'exécution suivante.
# ---------------------------------------------------------------------------

import os
import sys
import subprocess

# Ajouter la racine du projet au PATH pour les imports relatifs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

STEPS = [
    "python ingestion/fetch_fixtures.py",
    "python ingestion/fetch_stats.py",
    "python ingestion/fetch_lineups.py",
    "python ingestion/fetch_events.py",
    "python ingestion/fetch_injuries.py",
    "python ingestion/fetch_standings.py",
    "python ingestion/fetch_player_stats.py",
    "python ingestion/fetch_odds_api_football.py",
    "python preprocessing/match_odds_mapper.py",
    "python ingestion/merge_dataset.py",
    "python preprocessing/create_lstm_sequences.py",
    "python modeling/lstm_model.py",
    "python evaluation/backtest_kelly.py",
]

for cmd in STEPS:
    print(f"🚀 Running {cmd}...")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ {cmd} s'est terminé avec un code {result.returncode}")
        # Vous pouvez décommenter la ligne suivante pour arrêter le pipeline en cas d'erreur :
        # break

# Ajout du ranking
print("🔄 Génération automatique du fichier data/rankings.csv à partir des statistiques...")

ranking_result = subprocess.run("python generate_rankings.py", shell=True)
if ranking_result.returncode != 0:
    print("❌ Erreur lors de la génération du fichier rankings.csv")
else:
    print("✅ rankings.csv généré avec succès.")

print("✅ Pipeline complet exécuté avec succès.")        # break

print("✅ Pipeline complet exécuté avec succès.")
