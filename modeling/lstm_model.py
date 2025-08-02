# modeling/lstm_model.py
# -----------------------------------------------------------------------------
# Entraîne un modèle LSTM sur les données séquentielles générées
# -----------------------------------------------------------------------------

import os
import numpy as np

X_PATH = "data/lstm/X.npy"
Y_PATH = "data/lstm/y.npy"
OUTPUT_PATH = "data/lstm/y_pred_proba.npy"

# Vérifie que les fichiers existent
if not os.path.exists(X_PATH) or not os.path.exists(Y_PATH):
    print("❌ Données d'entraînement manquantes. Lance d'abord preprocessing/create_lstm_sequences.py")
    exit()

try:
    X = np.load(X_PATH)
    y = np.load(Y_PATH)

    if len(X) == 0 or len(y) == 0:
        print("❌ Données vides. Vérifie preprocessing/create_lstm_sequences.py")
        exit()

    # 🔽 Exemple minimal — à remplacer par ton vrai modèle
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(max_iter=200)
    model.fit(X, y)

    proba = model.predict_proba(X)
    np.save(OUTPUT_PATH, proba)

    print(f"✅ Prédictions sauvegardées dans : {OUTPUT_PATH}")
except Exception as e:
    print(f"❌ Erreur dans lstm_model.py : {e}")
