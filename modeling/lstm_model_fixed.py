#!/usr/bin/env python3
# modeling/lstm_model_fixed.py
# -----------------------------------------------------------------------------
# Entraîne un modèle LSTM et génère des prédictions pour les matchs d'aujourd'hui
# -----------------------------------------------------------------------------

import os
import numpy as np
import pandas as pd

# Import TensorFlow
try:
    import tensorflow as tf
except ImportError as exc:
    raise ImportError(
        "TensorFlow est requis pour entraîner le modèle LSTM. "
        "Installez-le avec: pip install tensorflow"
    ) from exc

# Chemins des fichiers
X_TRAIN_PATH = "data/lstm/X.npy"
Y_TRAIN_PATH = "data/lstm/y.npy"
X_TODAY_PATH = "data/lstm/X_today.npy"
TEAMS_PATH = "data/lstm/team_pairs.csv"
OUTPUT_PATH = "data/lstm/y_pred_proba.npy"
PREDICTIONS_CSV = "data/lstm/predictions_today.csv"

def load_data():
    """Charge toutes les données nécessaires"""
    # Vérifier l'existence des fichiers
    required_files = [X_TRAIN_PATH, Y_TRAIN_PATH, X_TODAY_PATH, TEAMS_PATH]
    for filepath in required_files:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"❌ Fichier manquant : {filepath}")
    
    X_train = np.load(X_TRAIN_PATH)
    y_train = np.load(Y_TRAIN_PATH)
    X_today = np.load(X_TODAY_PATH)
    teams_df = pd.read_csv(TEAMS_PATH)
    
    if X_train.size == 0 or y_train.size == 0:
        raise ValueError("❌ Données d'entraînement vides")
    
    return X_train, y_train, X_today, teams_df

def build_model(timesteps, n_features, n_classes=3):
    """Construit un modèle LSTM optimisé"""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(timesteps, n_features)),
        tf.keras.layers.LSTM(64, return_sequences=True, dropout=0.2),
        tf.keras.layers.LSTM(32, dropout=0.2),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(n_classes, activation="softmax"),
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    return model

def train_model(model, X_train, y_train):
    """Entraîne le modèle LSTM"""
    print("🚀 Début de l'entraînement du modèle LSTM...")
    
    # Callback pour arrêter l'entraînement si pas d'amélioration
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='loss',
        patience=5,
        restore_best_weights=True
    )
    
    # Entraînement
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stopping],
        verbose=1
    )
    
    return history

def main():
    """Fonction principale"""
    try:
        # 1. Charger les données
        X_train, y_train, X_today, teams_df = load_data()
        timesteps, n_features = X_train.shape[1], X_train.shape[2]
        
        print(f"✅ Données chargées:")
        print(f"   - Entraînement: {X_train.shape} samples, {np.unique(y_train)} classes")
        print(f"   - Matchs aujourd'hui: {X_today.shape}")
        
        # 2. Construire le modèle
        model = build_model(timesteps, n_features)
        print(f"✅ Modèle LSTM construit avec {timesteps} timesteps, {n_features} features")
        
        # 3. Entraîner le modèle
        history = train_model(model, X_train, y_train)
        print(f"✅ Entraînement terminé")
        
        # 4. Prédictions sur les matchs d'aujourd'hui
        print("🎯 Génération des prédictions pour les matchs d'aujourd'hui...")
        predictions_proba = model.predict(X_today, verbose=0)
        
        # 5. Sauvegarder les probabilités brutes
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        np.save(OUTPUT_PATH, predictions_proba)
        
        # 6. Créer un CSV lisible avec les prédictions
        results = []
        for i, (_, row) in enumerate(teams_df.iterrows()):
            home_team = row['home_team']
            away_team = row['away_team']
            
            prob_home = predictions_proba[i][0]
            prob_draw = predictions_proba[i][1] 
            prob_away = predictions_proba[i][2]
            
            # Prédiction la plus probable
            predicted_outcome = ["Home", "Draw", "Away"][np.argmax(predictions_proba[i])]
            confidence = np.max(predictions_proba[i])
            
            results.append({
                "match": f"{home_team} vs {away_team}",
                "home_team": home_team,
                "away_team": away_team,
                "prob_home": round(prob_home, 3),
                "prob_draw": round(prob_draw, 3),
                "prob_away": round(prob_away, 3),
                "predicted_outcome": predicted_outcome,
                "confidence": round(confidence, 3)
            })
        
        # Sauvegarder le CSV des prédictions
        predictions_df = pd.DataFrame(results)
        predictions_df.to_csv(PREDICTIONS_CSV, index=False)
        
        print(f"✅ Prédictions sauvegardées:")
        print(f"   - Probabilités: {OUTPUT_PATH}")
        print(f"   - CSV détaillé: {PREDICTIONS_CSV}")
        
        # 7. Afficher un aperçu des prédictions
        print(f"\n🎲 Aperçu des prédictions:")
        for i, result in enumerate(results[:5]):  # Afficher les 5 premiers
            print(f"   {i+1}. {result['match']}")
            print(f"      Home: {result['prob_home']:.1%} | Draw: {result['prob_draw']:.1%} | Away: {result['prob_away']:.1%}")
            print(f"      Prédiction: {result['predicted_outcome']} ({result['confidence']:.1%})")
            print()
        
        if len(results) > 5:
            print(f"   ... et {len(results) - 5} autres matchs")
        
    except Exception as e:
        print(f"❌ Erreur dans lstm_model_fixed.py : {e}")
        raise

if __name__ == "__main__":
    main()