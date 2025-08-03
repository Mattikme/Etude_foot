# modeling/lstm_model.py
# -----------------------------------------------------------------------------
# Entraîne un modèle LSTM sur les données séquentielles générées
# -----------------------------------------------------------------------------

"""
Ce module charge des séquences d'entraînement et une cible issue du pré‑traitement
et entraîne un réseau de neurones de type LSTM pour prédire l'issue d'un match
(victoire domicile, match nul ou victoire extérieure).  Il remplace l'exemple
minimal qui utilisait une régression logistique par un modèle de deep‑learning
plus cohérent avec la description du projet.

Les fichiers `X.npy` et `y.npy` sont supposés être générés par
`preprocessing/create_lstm_sequences.py`.  `X` doit avoir la forme
`(n_samples, timesteps, n_features)`.  Si vous avez créé un tableau à une ou
deux dimensions, le script le remodèle automatiquement.
"""

import os
import numpy as np

# Essayez d'importer TensorFlow.  S'il n'est pas installé, informez l'utilisateur.
try:
    import tensorflow as tf
except ImportError as exc:
    raise ImportError(
        "TensorFlow est requis pour entraîner le modèle LSTM. "
        "Ajoutez `tensorflow` dans requirements.txt et installez‑le."
    ) from exc

X_PATH = "data/lstm/X.npy"
Y_PATH = "data/lstm/y.npy"
OUTPUT_PATH = "data/lstm/y_pred_proba.npy"


def load_data() -> tuple[np.ndarray, np.ndarray]:
    """Charge les fichiers de données et effectue quelques vérifications."""
    if not os.path.exists(X_PATH) or not os.path.exists(Y_PATH):
        raise FileNotFoundError(
            "Données d'entraînement manquantes. Lancez d'abord preprocessing/create_lstm_sequences.py"
        )
    X = np.load(X_PATH)
    y = np.load(Y_PATH)
    if X.size == 0 or y.size == 0:
        raise ValueError(
            "Données vides. Vérifiez preprocessing/create_lstm_sequences.py pour générer des séquences non vides."
        )
    # S'assurer que y est un vecteur
    y = y.reshape(-1)
    # Remise en forme éventuelle de X en (n_samples, timesteps, n_features)
    if X.ndim == 1:
        # Tableau de valeurs scalaires
        X = X.reshape(-1, 1, 1)
    elif X.ndim == 2:
        # (n_samples, n_features) → on considère chaque feature comme un pas de temps unique
        n_samples, n_features = X.shape
        X = X.reshape(n_samples, n_features, 1)
    return X, y


def build_model(timesteps: int, n_features: int, n_classes: int = 3) -> tf.keras.Model:
    """Construit un modèle LSTM simple."""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(timesteps, n_features)),
        tf.keras.layers.LSTM(64),
        tf.keras.layers.Dense(n_classes, activation="softmax"),
    ])
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main() -> None:
    try:
        X, y = load_data()
        timesteps, n_features = X.shape[1], X.shape[2]
        model = build_model(timesteps, n_features)
        # Entraînement rapide ; ajustez epochs et batch_size selon vos besoins
        model.fit(X, y, epochs=10, batch_size=32, verbose=2)
        proba = model.predict(X)
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        np.save(OUTPUT_PATH, proba)
        print(f"✅ Prédictions sauvegardées dans : {OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Erreur dans lstm_model.py : {e}")


if __name__ == "__main__":
    main()