# pipeline/run_pipeline.py
# ---------------------------------------------------------------------------
# Orchestration complète du pipeline de paris football : ingestion, traitement,
# analyse des value bets et évaluation des résultats précédents.
# ---------------------------------------------------------------------------

import os
import sys
import subprocess
from datetime import datetime, timedelta

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
    "python preprocessing/generate_rankings.py",  # ✅ Appelé ici une seule fois
    "python evaluation/backtest_kelly.py",
]

for cmd in STEPS:
    print(f"🚀 Running {cmd}...")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ {cmd} s'est terminé avec un code {result.returncode}")
        # break

# Analyse des paris du jour
print("🔍 Analyse des value bets en cours...")
analyse_result = subprocess.run("python analyse_bets.py", shell=True)
if analyse_result.returncode != 0:
    print("❌ Erreur lors de l'analyse des value bets.")
else:
    print("✅ Fichier de paris généré : data/bets_today.csv")

# Évaluation des paris de la veille
yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
bets_yesterday = f"data/bets_{yesterday}.csv"
if os.path.exists(bets_yesterday):
    print(f"📊 Évaluation des résultats de paris pour {yesterday}...")
    result = subprocess.run("python evaluate_bets.py", shell=True)
    if result.returncode != 0:
        print("❌ Erreur dans evaluate_bets.py")
else:
    print(f"ℹ️ Aucun pari trouvé pour hier ({yesterday}), évaluation ignorée.")

print("✅ Pipeline complet exécuté avec succès.") 
