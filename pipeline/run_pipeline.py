# pipeline/run_pipeline.py
# -----------------------------------------------------------------------------
# Ce script orchestre l'exécution complète du projet :
# - Récupération des données (API-Football & Pinnacle)
# - Prétraitement, création des séquences LSTM
# - Entraînement du modèle, prédictions, et backtest
# -----------------------------------------------------------------------------

import os
import sys

# Ajouter la racine du projet au PATH pour les imports relatifs (ex: utils)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

steps = [
    "ingestion/fetch_fixtures.py",
    "ingestion/fetch_stats.py",
    "ingestion/fetch_lineups.py",
    "ingestion/fetch_events.py",
    "ingestion/fetch_injuries.py",
    "ingestion/fetch_standings.py",
    "ingestion/fetch_player_stats.py",
    "ingestion/fetch_pinnacle_odds.py",
    "preprocessing/match_odds_mapper.py",
    "ingestion/merge_dataset.py",
    "preprocessing/create_lstm_sequences.py",
    "modeling/lstm_model.py",
    "evaluation/backtest_kelly.py"
]

for step in steps:
    print(f"🚀 Running {step}...")
    os.system(f"python {step}")

print("✅ Pipeline complet exécuté avec succès.")
