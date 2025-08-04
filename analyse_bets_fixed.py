#!/usr/bin/env python3
# analyse_bets_fixed.py
# ---------------------------------------------------------------------------
# Analyse les value bets en utilisant les prédictions LSTM et les cotes API
# Combine les probabilités prédites par le modèle avec les cotes des bookmakers
# ---------------------------------------------------------------------------

import os
import json
import pandas as pd
import numpy as np
from glob import glob
from datetime import datetime

# Constantes
TODAY = datetime.today().strftime("%Y-%m-%d")
ODDS_PATHS = glob(f"data/raw/odds_*.json")
PREDICTIONS_PATH = "data/lstm/predictions_today.csv"
OUTPUT_PATH = "data/bets_today.csv"

def load_predictions():
    """Charge les prédictions LSTM du jour"""
    if not os.path.exists(PREDICTIONS_PATH):
        raise FileNotFoundError(f"❌ Fichier de prédictions introuvable : {PREDICTIONS_PATH}")
    
    predictions_df = pd.read_csv(PREDICTIONS_PATH)
    print(f"✅ {len(predictions_df)} prédictions LSTM chargées")
    return predictions_df

def load_fixture_mapping():
    """Crée un mapping fixture_id -> noms des équipes"""
    fixtures_files = glob("data/raw/fixtures_*_2025-08-04.json")
    fixture_mapping = {}
    
    for fixtures_file in fixtures_files:
        try:
            with open(fixtures_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for match in data.get("response", []):
                fixture_id = match.get("fixture", {}).get("id")
                home_team = match.get("teams", {}).get("home", {}).get("name")
                away_team = match.get("teams", {}).get("away", {}).get("name")
                
                if fixture_id and home_team and away_team:
                    fixture_mapping[fixture_id] = f"{home_team} vs {away_team}"
                    
        except Exception as e:
            print(f"⚠️ Erreur lecture fixtures {fixtures_file}: {e}")
            continue
    
    return fixture_mapping

def load_odds_data():
    """Charge et structure les données de cotes"""
    if not ODDS_PATHS:
        raise FileNotFoundError("❌ Aucun fichier de cotes trouvé dans data/raw/")
    
    # Charger le mapping fixture_id -> équipes
    fixture_mapping = load_fixture_mapping()
    all_odds = {}
    
    for odds_path in ODDS_PATHS:
        try:
            with open(odds_path, "r", encoding="utf-8") as f:
                odds_data = json.load(f)
            
            # Extraire les cotes Bet365 pour chaque match
            for match_odds in odds_data.get("response", []):
                if "bookmakers" not in match_odds:
                    continue
                
                # Récupérer fixture_id et les noms des équipes
                fixture_id = match_odds.get("fixture", {}).get("id")
                if fixture_id not in fixture_mapping:
                    continue
                
                match_key = fixture_mapping[fixture_id]
                
                # Chercher les cotes Bet365
                for bookmaker in match_odds["bookmakers"]:
                    if bookmaker["name"] == "Bet365":
                        for market in bookmaker["bets"]:
                            if market["name"] == "Match Winner":
                                odds_dict = {}
                                for outcome in market["values"]:
                                    if outcome["value"] == "Home":
                                        odds_dict["odds_home"] = float(outcome["odd"])
                                    elif outcome["value"] == "Draw":
                                        odds_dict["odds_draw"] = float(outcome["odd"])
                                    elif outcome["value"] == "Away":
                                        odds_dict["odds_away"] = float(outcome["odd"])
                                
                                if len(odds_dict) == 3:  # Toutes les cotes présentes
                                    all_odds[match_key] = odds_dict
                                    break
                        break
                        
        except Exception as e:
            print(f"⚠️ Erreur lecture cotes {odds_path}: {e}")
            continue
    
    print(f"✅ {len(all_odds)} matchs avec cotes chargés")
    return all_odds

def calculate_value_bets(predictions_df, odds_dict):
    """Calcule les value bets basés sur les prédictions LSTM et cotes"""
    value_bets = []
    
    for _, prediction in predictions_df.iterrows():
        match_name = prediction["match"]
        
        # Rechercher les cotes pour ce match
        if match_name not in odds_dict:
            print(f"⚠️ Cotes manquantes pour : {match_name}")
            continue
        
        odds = odds_dict[match_name]
        
        # Probabilités prédites par LSTM
        prob_home = prediction["prob_home"]
        prob_draw = prediction["prob_draw"] 
        prob_away = prediction["prob_away"]
        
        # Calculer les value bets pour chaque issue
        outcomes = [
            ("Home", prob_home, odds["odds_home"]),
            ("Draw", prob_draw, odds["odds_draw"]),
            ("Away", prob_away, odds["odds_away"])
        ]
        
        for outcome_name, predicted_prob, bookmaker_odd in outcomes:
            # Expected Value = (Cote × Probabilité prédite) - 1
            expected_value = (bookmaker_odd * predicted_prob) - 1
            
            # Seuil minimum pour considérer comme value bet
            if expected_value > 0.05:  # 5% de value minimum
                value_bets.append({
                    "match": match_name,
                    "bet_on": outcome_name,
                    "bookmaker_odds": bookmaker_odd,
                    "expected_prob": round(predicted_prob, 3),
                    "expected_value": round(expected_value, 3),
                    "implied_odds_prob": round(1/bookmaker_odd, 3),
                    "edge": round((predicted_prob - 1/bookmaker_odd) * 100, 2)  # Avantage en %
                })
    
    return value_bets

def main():
    """Analyse principale des value bets"""
    try:
        # 1. Charger les prédictions LSTM
        predictions_df = load_predictions()
        
        # 2. Charger les cotes des bookmakers
        odds_dict = load_odds_data()
        
        # 3. Calculer les value bets
        value_bets = calculate_value_bets(predictions_df, odds_dict)
        
        if not value_bets:
            print("ℹ️ Aucun value bet détecté aujourd'hui avec les critères actuels.")
            # Créer un fichier vide pour éviter les erreurs downstream
            pd.DataFrame().to_csv(OUTPUT_PATH, index=False)
            return
        
        # 4. Créer le DataFrame et trier par expected_value décroissant
        value_bets_df = pd.DataFrame(value_bets)
        value_bets_df = value_bets_df.sort_values("expected_value", ascending=False)
        
        # 5. Sauvegarder les résultats
        os.makedirs(os.path.dirname(OUTPUT_PATH) if os.path.dirname(OUTPUT_PATH) else ".", exist_ok=True)
        value_bets_df.to_csv(OUTPUT_PATH, index=False)
        
        print(f"✅ {len(value_bets_df)} value bets enregistrés dans {OUTPUT_PATH}")
        
        # 6. Afficher les meilleurs value bets
        print(f"\n💰 Top 5 Value Bets du jour:")
        for i, (_, bet) in enumerate(value_bets_df.head().iterrows()):
            print(f"   {i+1}. {bet['match']}")
            print(f"      Pari: {bet['bet_on']} @ {bet['bookmaker_odds']}")
            print(f"      Prob. LSTM: {bet['expected_prob']:.1%} vs Implied: {bet['implied_odds_prob']:.1%}")
            print(f"      Expected Value: +{bet['expected_value']:.1%} | Edge: +{bet['edge']:.1f}%")
            print()
        
        # 7. Statistiques globales
        total_value = value_bets_df["expected_value"].sum()
        avg_odds = value_bets_df["bookmaker_odds"].mean()
        
        print(f"📊 Statistiques:")
        print(f"   - Value total cumulé: +{total_value:.1%}")
        print(f"   - Cote moyenne des bets: {avg_odds:.2f}")
        print(f"   - Edge moyen: +{value_bets_df['edge'].mean():.1f}%")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse des value bets : {e}")
        raise

if __name__ == "__main__":
    main()