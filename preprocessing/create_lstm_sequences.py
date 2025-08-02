# preprocessing/create_lstm_sequences.py
# -----------------------------------------------------------------------------
# Ce script prépare les données pour l'entraînement d'un modèle LSTM.
# Il transforme le jeu de données en séquences temporelles par équipe,
# avec glissement sur N matchs précédents, normalisation, et étiquetage.
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np
import os

WINDOW_SIZE = 5
LABEL_COL = "outcome"

# Chargement du fichier de base fusionné
base_df = pd.read_csv("data/processed/base_matches.csv")

# Création de la colonne cible : 1 = victoire domicile, 0 = nul, -1 = défaite domicile
base_df[LABEL_COL] = np.select(
    [base_df["goals_home"] > base_df["goals_away"],
     base_df["goals_home"] == base_df["goals_away"]],
    [1, 0],
    default=-1
)

# Ordre temporel
base_df.sort_values("date", inplace=True)

# Séquences simples pour prototypage : chaque ligne devient une fenêtre de N matchs précédents
sequences = []
labels = []
for i in range(WINDOW_SIZE, len(base_df)):
    window = base_df.iloc[i - WINDOW_SIZE:i]
    if LABEL_COL in base_df.columns:
        label = base_df.iloc[i][LABEL_COL]
        features = window[["goals_home", "goals_away"]].values.flatten()
        sequences.append(features)
        labels.append(label)

# Sauvegarde des jeux X, y
os.makedirs("data/lstm", exist_ok=True)
np.save("data/lstm/X.npy", np.array(sequences))
np.save("data/lstm/y.npy", np.array(labels))

print("✅ Séquences LSTM générées dans data/lstm/")
