# preprocessing/create_lstm_sequences.py
# -----------------------------------------------------------------------------
# Transforme les données fusionnées en séquences prêtes pour le LSTM
# -----------------------------------------------------------------------------

import os
import pandas as pd
import numpy as np

INPUT_FILE = "data/processed/base_matches.csv"
OUTPUT_DIR = "data/lstm"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Vérifier que le fichier existe
if not os.path.exists(INPUT_FILE):
    print(f"❌ Fichier introuvable : {INPUT_FILE}")
    exit()

try:
    base_df = pd.read_csv(INPUT_FILE)

    if base_df.empty:
        print(f"⚠️ Fichier vide : {INPUT_FILE}")
        exit()

    # Exemple minimal de transformation — à adapter selon ta structure
    # Ici, on encode juste le résultat match
    base_df = base_df.dropna(subset=["teams.home.name", "teams.away.name", "goals.home", "goals.away"])
    base_df["result"] = np.where(base_df["goals.home"] > base_df["goals.away"], 0,
                          np.where(base_df["goals.home"] < base_df["goals.away"], 2, 1))

    X = np.arange(len(base_df)).reshape(-1, 1)  # Placeholder : remplace par vraies features
    y = base_df["result"].values

    np.save(os.path.join(OUTPUT_DIR, "X.npy"), X)
    np.save(os.path.join(OUTPUT_DIR, "y.npy"), y)

    print(f"✅ Séquences LSTM sauvegardées dans {OUTPUT_DIR}")
except pd.errors.EmptyDataError:
    print(f"❌ Fichier CSV vide (aucune colonne lisible) : {INPUT_FILE}")
except Exception as e:
    print(f"❌ Erreur lors de la génération des séquences : {e}")
