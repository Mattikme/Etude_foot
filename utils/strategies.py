import json
import os
import pandas as pd


def calculate_goal_stats(stats: dict) -> float:
    """
    Calcule le score de forme basé sur les buts marqués et encaissés.
    """
    gf = stats.get("goals_for", 0)
    ga = stats.get("goals_against", 0)
    return gf - ga


def load_rankings(path: str = "data/rankings.csv") -> pd.DataFrame:
    """
    Charge le classement global (similaire ELO ou autres).
    """
    return pd.read_csv(path, index_col=0)


def estimate_probabilities(home_stats: dict, away_stats: dict, home_team: str, away_team: str, rankings: pd.DataFrame) -> dict:
    """
    Évalue les probabilités de victoire/défaite/nul inspiré de la stratégie PL.
    """
    home_score = calculate_goal_stats(home_stats)
    away_score = calculate_goal_stats(away_stats)

    # Bonus domicile
    home_score += 0.5

    # Ajustement par ranking
    if home_team in rankings.index:
        home_score += rankings.loc[home_team]["score"] / 1000
    if away_team in rankings.index:
        away_score += rankings.loc[away_team]["score"] / 1000

    # Total et normalisation
    total = home_score + away_score
    if total == 0:
        return {"home": 0.33, "draw": 0.34, "away": 0.33}  # fallback

    home_prob = home_score / total
    away_prob = away_score / total
    draw_prob = 1 - (home_prob + away_prob)
    draw_prob = max(0, min(draw_prob, 0.5))  # borne

    return {
        "home": round(home_prob, 3),
        "draw": round(draw_prob, 3),
        "away": round(away_prob, 3),
    }
