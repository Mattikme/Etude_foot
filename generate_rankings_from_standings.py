#!/usr/bin/env python3
# generate_rankings_from_standings.py
# ---------------------------------------------------------------------------
# Génère un fichier rankings.csv basé sur les standings des ligues
# Utilise les données de classement (points, goals diff, etc.) pour calculer
# la force relative des équipes
# ---------------------------------------------------------------------------

import os
import json
import pandas as pd
from glob import glob

def calculate_team_strength(standing):
    """
    Calcule un score de force d'équipe basé sur les standings
    """
    try:
        # Récupération des métriques de base
        points = standing.get("points", 0)
        goals_diff = standing.get("goalsDiff", 0)
        played = standing["all"]["played"] or 1  # éviter division par 0
        wins = standing["all"]["win"]
        draws = standing["all"]["draw"]
        
        # Score basé sur différents facteurs
        # Points par match (plus important)
        points_per_game = points / played
        
        # Ratio victoires
        win_rate = wins / played
        
        # Goals différentiel normalisé
        goal_diff_per_game = goals_diff / played
        
        # Score composite (sur 1000 comme un système ELO)
        base_score = 500  # Score de base
        points_bonus = points_per_game * 150  # Max ~450 pts
        win_bonus = win_rate * 200  # Max 200 pts  
        goal_bonus = goal_diff_per_game * 50  # Peut être négatif
        
        final_score = base_score + points_bonus + win_bonus + goal_bonus
        return max(100, int(final_score))  # Score minimum de 100
        
    except (KeyError, TypeError, ZeroDivisionError):
        return 500  # Score neutre par défaut

def generate_rankings():
    """
    Génère le fichier rankings.csv basé sur les standings
    """
    standings_files = glob("data/raw/standings/standings_*_2024.json")
    
    if not standings_files:
        print("❌ Aucun fichier de standings trouvé dans data/raw/standings/")
        return
    
    all_teams = []
    
    for file_path in standings_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Extraire les standings
            for league_data in data.get("response", []):
                standings = league_data.get("league", {}).get("standings", [[]])
                for group in standings:  # Parfois il y a plusieurs groupes
                    for team_standing in group:
                        team_name = team_standing["team"]["name"]
                        strength_score = calculate_team_strength(team_standing)
                        
                        all_teams.append({
                            "team": team_name,
                            "ranking": strength_score
                        })
                        
        except Exception as e:
            print(f"⚠️ Erreur lors du traitement de {file_path}: {e}")
            continue
    
    if not all_teams:
        print("❌ Aucune donnée d'équipe extraite des standings")
        return
    
    # Créer le DataFrame et éliminer les doublons
    df = pd.DataFrame(all_teams)
    
    # Grouper par équipe et prendre la moyenne (au cas où une équipe apparait dans plusieurs ligues)
    df = df.groupby("team")["ranking"].mean().reset_index()
    
    # Trier par ranking décroissant (meilleur ranking = score plus élevé)
    df = df.sort_values("ranking", ascending=False)
    
    # Sauvegarder
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/rankings.csv", index=False)
    
    print(f"✅ {len(df)} équipes enregistrées dans data/rankings.csv")
    print(f"🏆 Top 5 équipes:")
    for i, row in df.head().iterrows():
        print(f"   {i+1}. {row['team']} - Score: {row['ranking']:.1f}")

if __name__ == "__main__":
    generate_rankings()