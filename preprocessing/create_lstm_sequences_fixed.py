#!/usr/bin/env python3
# preprocessing/create_lstm_sequences_fixed.py
# -----------------------------------------------------------------------------
# Crée des séquences LSTM basées sur les rankings et matchs actuels
# Simule des données d'entraînement et prépare les prédictions pour aujourd'hui
# -----------------------------------------------------------------------------

import os
import pandas as pd
import numpy as np

INPUT_FILE = "data/processed/base_matches.csv"
RANKINGS_FILE = "data/rankings.csv"
OUTPUT_DIR = "data/lstm"

def load_data():
    """Charge les données de matchs et rankings"""
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"❌ Fichier introuvable : {INPUT_FILE}")
    
    if not os.path.exists(RANKINGS_FILE):
        raise FileNotFoundError(f"❌ Fichier introuvable : {RANKINGS_FILE}")
    
    matches_df = pd.read_csv(INPUT_FILE)
    rankings_df = pd.read_csv(RANKINGS_FILE)
    
    if matches_df.empty:
        raise ValueError(f"⚠️ Fichier de matchs vide : {INPUT_FILE}")
    
    # Créer un dictionnaire de rankings pour mapping rapide
    rankings_dict = dict(zip(rankings_df["team"], rankings_df["ranking"]))
    
    return matches_df, rankings_dict

def create_features(matches_df, rankings_dict):
    """Crée les features pour le modèle LSTM basées sur les rankings"""
    features = []
    team_pairs = []
    
    for _, match in matches_df.iterrows():
        home_team = match["teams.home.name"]
        away_team = match["teams.away.name"]
        
        # Récupérer les rankings (score neutre si équipe inconnue)
        home_ranking = rankings_dict.get(home_team, 500)
        away_ranking = rankings_dict.get(away_team, 500)
        
        # Features basiques
        ranking_diff = home_ranking - away_ranking  # Positif = domicile plus fort
        ranking_sum = home_ranking + away_ranking    # Force globale du match
        home_advantage = 50  # Avantage domicile fixe
        
        # Feature vector pour ce match
        match_features = [
            ranking_diff / 1000,      # Normaliser
            ranking_sum / 2000,       # Normaliser  
            home_advantage / 100,     # Normaliser
            home_ranking / 1000,      # Ranking domicile normalisé
            away_ranking / 1000,      # Ranking extérieur normalisé
        ]
        
        features.append(match_features)
        team_pairs.append((home_team, away_team))
    
    return np.array(features), team_pairs

def simulate_training_data(n_samples=1000):
    """Simule des données d'entraînement historiques"""
    np.random.seed(42)  # Pour reproductibilité
    
    # Générer des features aléatoires mais cohérentes
    X_train = []
    y_train = []
    
    for _ in range(n_samples):
        # Simuler des rankings d'équipes
        home_rank = np.random.normal(700, 200)  # Centré sur 700 ± 200
        away_rank = np.random.normal(700, 200)
        
        # Contraindre dans une plage raisonnable
        home_rank = max(100, min(1300, home_rank))
        away_rank = max(100, min(1300, away_rank))
        
        # Features similaires à celles réelles
        ranking_diff = home_rank - away_rank
        ranking_sum = home_rank + away_rank
        home_advantage = 50
        
        features = [
            ranking_diff / 1000,
            ranking_sum / 2000,
            home_advantage / 100,
            home_rank / 1000,
            away_rank / 1000,
        ]
        
        # Simuler un résultat basé sur les rankings + aléa
        prob_home = 0.45 + (ranking_diff / 2000)  # Base 45% + diff ranking
        prob_away = 0.35 - (ranking_diff / 3000)  # Base 35% - diff ranking  
        prob_draw = 1.0 - prob_home - prob_away
        
        # Contraindre les probabilités
        prob_home = max(0.1, min(0.8, prob_home))
        prob_away = max(0.1, min(0.8, prob_away))
        prob_draw = max(0.1, min(0.8, prob_draw))
        
        # Normaliser pour que la somme soit exactement 1
        total = prob_home + prob_draw + prob_away
        prob_home /= total
        prob_draw /= total
        prob_away /= total
        
        # Choisir le résultat selon ces probabilités
        outcome = np.random.choice(3, p=[prob_home, prob_draw, prob_away])
        
        X_train.append(features)
        y_train.append(outcome)
    
    return np.array(X_train), np.array(y_train)

def main():
    """Génère les séquences LSTM pour entraînement et prédiction"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # 1. Charger les données réelles
        matches_df, rankings_dict = load_data()
        print(f"✅ Chargé {len(matches_df)} matchs et {len(rankings_dict)} équipes")
        
        # 2. Créer les features pour les matchs d'aujourd'hui  
        X_today, team_pairs = create_features(matches_df, rankings_dict)
        print(f"✅ Créé features pour {len(X_today)} matchs d'aujourd'hui")
        
        # 3. Simuler des données d'entraînement historiques
        X_train, y_train = simulate_training_data(n_samples=1000)
        print(f"✅ Simulé {len(X_train)} échantillons d'entraînement")
        
        # 4. Préparer les données pour LSTM (reshape en 3D)
        # Pour LSTM : (n_samples, timesteps, n_features)
        # Ici on a 1 timestep, 5 features
        X_train_reshaped = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
        X_today_reshaped = X_today.reshape(X_today.shape[0], 1, X_today.shape[1])
        
        # 5. Sauvegarder les données
        np.save(os.path.join(OUTPUT_DIR, "X.npy"), X_train_reshaped)
        np.save(os.path.join(OUTPUT_DIR, "y.npy"), y_train)
        np.save(os.path.join(OUTPUT_DIR, "X_today.npy"), X_today_reshaped)
        
        # Sauvegarder les noms des équipes pour référence
        team_pairs_df = pd.DataFrame(team_pairs, columns=["home_team", "away_team"])
        team_pairs_df.to_csv(os.path.join(OUTPUT_DIR, "team_pairs.csv"), index=False)
        
        print(f"✅ Données LSTM sauvegardées dans {OUTPUT_DIR}")
        print(f"   - X.npy: données d'entraînement {X_train_reshaped.shape}")  
        print(f"   - y.npy: résultats d'entraînement {y_train.shape}")
        print(f"   - X_today.npy: matchs d'aujourd'hui {X_today_reshaped.shape}")
        print(f"   - team_pairs.csv: noms des équipes")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des séquences : {e}")
        raise

if __name__ == "__main__":
    main()