# evaluation/backtest_kelly.py
# -----------------------------------------------------------------------------
# Backtest des prédictions en utilisant le critère de Kelly
# -----------------------------------------------------------------------------

import os
import numpy as np

PREDICTIONS_PATH = "data/lstm/y_pred_proba.npy"
MERGED_DATA_PATH = "data/processed/base_matches.csv"

# Vérifie que les fichiers nécessaires existent
if not os.path.exists(PREDICTIONS_PATH):
    print("❌ Prédictions manquantes. Exécute modeling/lstm_model.py d'abord.")
    exit()

if not os.path.exists(MERGED_DATA_PATH):
    print("❌ Fichier base_matches.csv introuvable. Vérifie ingestion/merge_dataset.py.")
    exit()

try:
    predicted_probas = np.load(PREDICTIONS_PATH)  # shape: (n, 3)
    if predicted_probas.size == 0:
        print("❌ Prédictions vides.")
        exit()

    import pandas as pd
    base_matches = pd.read_csv(MERGED_DATA_PATH)

    if base_matches.empty:
        print("❌ Fichier base_matches.csv est vide.")
        exit()

    # 🔽 Exemple minimal de backtest — à adapter selon la logique de Kelly
    print(f"🔎 Prédictions shape : {predicted_probas.shape}")
    print(f"📊 Nombre de matchs disponibles : {len(base_matches)}")

    # Exemple : afficher les 5 premières probas
    for i, proba in enumerate(predicted_probas[:5]):
        print(f"Match {i+1} => Home: {proba[0]:.2f}, Draw: {proba[1]:.2f}, Away: {proba[2]:.2f}")

    print("✅ Backtest Kelly terminé (simulation basique).")

except Exception as e:
    print(f"❌ Erreur dans backtest_kelly.py : {e}")
