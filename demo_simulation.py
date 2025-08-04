#!/usr/bin/env python3
# demo_simulation.py
# ---------------------------------------------------------------------------
# Script de simulation pour démontrer le système avec des données historiques
# ---------------------------------------------------------------------------

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from betting_tracker import BettingTracker

def create_demo_history():
    """Crée un historique de démonstration avec 30 jours de données"""
    print("🎬 Création de données de démonstration...")
    
    tracker = BettingTracker()
    
    # Supprimer l'historique existant s'il existe
    if os.path.exists(tracker.history_file):
        os.remove(tracker.history_file)
    if os.path.exists(tracker.config_file):
        os.remove(tracker.config_file)
    
    # Réinitialiser
    tracker._initialize_files()
    
    # Générer 30 jours de données historiques
    start_date = datetime.now() - timedelta(days=30)
    
    # Ligues de démonstration
    demo_leagues = [
        "Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1",
        "Championship", "Eredivisie", "Primeira Liga", "Liga MX", "MLS"
    ]
    
    # Équipes de démonstration par ligue
    demo_teams = {
        "Premier League": ["Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United", "Newcastle"],
        "La Liga": ["Real Madrid", "Barcelona", "Atletico Madrid", "Sevilla", "Valencia", "Real Sociedad"],
        "Serie A": ["Inter Milan", "Juventus", "AC Milan", "Napoli", "AS Roma", "Lazio"],
        "Bundesliga": ["Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "Eintracht Frankfurt"],
        "Ligue 1": ["PSG", "Marseille", "Monaco", "Lyon", "Lille", "Nice"],
        "Championship": ["Leicester City", "Leeds United", "Southampton", "West Brom", "Middlesbrough"],
        "Eredivisie": ["Ajax", "PSV", "Feyenoord", "AZ Alkmaar", "FC Utrecht"],
        "Primeira Liga": ["Porto", "Benfica", "Sporting CP", "Braga", "Vitoria SC"],
        "Liga MX": ["Club America", "Chivas", "Cruz Azul", "Tigres", "Monterrey"],
        "MLS": ["LAFC", "Seattle Sounders", "Atlanta United", "New York City FC", "Toronto FC"]
    }
    
    all_bets = []
    current_bankroll = 1000.0
    total_bets = 0
    winning_bets = 0
    
    # Générer des paris pour chaque jour
    for day_offset in range(30):
        current_date = (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        
        # Nombre de paris par jour (0-8)
        daily_bets = random.randint(0, 8)
        
        if daily_bets == 0:
            continue
        
        day_profit = 0
        
        for bet_num in range(daily_bets):
            # Sélection aléatoire de ligue et équipes
            league = random.choice(demo_leagues)
            teams = demo_teams[league]
            
            if len(teams) >= 2:
                home_team = random.choice(teams)
                away_team = random.choice([t for t in teams if t != home_team])
                match_name = f"{home_team} vs {away_team}"
            else:
                match_name = f"Team A vs Team B"
            
            # Type de pari
            bet_on = random.choice(["Home", "Draw", "Away"])
            
            # Générer des cotes réalistes
            if bet_on == "Home":
                odds = round(random.uniform(1.5, 4.0), 2)
            elif bet_on == "Draw":
                odds = round(random.uniform(2.8, 4.5), 2)
            else:  # Away
                odds = round(random.uniform(1.8, 6.0), 2)
            
            # Mise
            bet_amount = random.uniform(5, 25)
            
            # Probabilité prédite (cohérente avec les cotes)
            implied_prob = 1 / odds
            predicted_prob = implied_prob + random.uniform(-0.1, 0.2)  # Edge simulé
            predicted_prob = max(0.1, min(0.9, predicted_prob))
            
            # Expected value
            expected_value = (odds * predicted_prob) - 1
            
            # Simuler le résultat (avec un bias pour les value bets positifs)
            if expected_value > 0.05:
                # Value bet - probabilité de gagner légèrement supérieure
                win_probability = predicted_prob * 1.1
            else:
                win_probability = predicted_prob * 0.9
            
            win_probability = max(0.05, min(0.95, win_probability))
            won = random.random() < win_probability
            
            # Calculer le profit/loss
            if won:
                profit_loss = bet_amount * (odds - 1)
                winning_bets += 1
            else:
                profit_loss = -bet_amount
            
            day_profit += profit_loss
            total_bets += 1
            
            # Créer l'entrée de pari
            bet_entry = {
                'date': current_date,
                'match': match_name,
                'league': league,
                'bet_on': bet_on,
                'odds': odds,
                'bet_amount': round(bet_amount, 2),
                'predicted_prob': round(predicted_prob, 3),
                'expected_value': round(expected_value, 3),
                'status': 'completed',
                'actual_result': bet_on if won else random.choice([r for r in ["Home", "Draw", "Away"] if r != bet_on]),
                'won': won,
                'profit_loss': round(profit_loss, 2),
                'bankroll_after': 0  # Sera calculé après
            }
            
            all_bets.append(bet_entry)
        
        # Mettre à jour le bankroll
        current_bankroll += day_profit
    
    # Calculer le bankroll après chaque pari
    running_bankroll = 1000.0
    for bet in all_bets:
        running_bankroll += bet['profit_loss']
        bet['bankroll_after'] = round(running_bankroll, 2)
    
    # Sauvegarder l'historique
    if all_bets:
        df = pd.DataFrame(all_bets)
        df.to_csv(tracker.history_file, index=False)
        
        # Mettre à jour la configuration
        config = tracker.get_config()
        config['current_bankroll'] = current_bankroll
        config['total_bets'] = total_bets
        config['winning_bets'] = winning_bets
        config['total_roi'] = current_bankroll - 1000.0
        tracker.save_config(config)
    
    print(f"✅ Historique de démonstration créé:")
    print(f"   📊 {total_bets} paris sur 30 jours")
    print(f"   🎯 {winning_bets} paris gagnants ({winning_bets/total_bets*100:.1f}%)")
    print(f"   💰 Bankroll final: {current_bankroll:.2f}€")
    print(f"   📈 ROI: {(current_bankroll-1000)/1000*100:+.1f}%")
    
    return tracker

def add_todays_pending_bets():
    """Ajoute les paris réels d'aujourd'hui en tant que paris en attente"""
    tracker = BettingTracker()
    
    # Vérifier s'il y a des value bets aujourd'hui
    if os.path.exists("data/bets_today.csv"):
        bets_df = pd.read_csv("data/bets_today.csv")
        if not bets_df.empty:
            print(f"\n💎 Ajout de {len(bets_df)} value bets d'aujourd'hui...")
            tracker.add_todays_bets(1.0)  # Mise normale
            
            stats = tracker.get_statistics()
            print(f"✅ Paris d'aujourd'hui ajoutés!")
            print(f"   📊 Paris en attente: {stats['pending_bets']}")
    
    return tracker

def main():
    """Fonction principale de démonstration"""
    print("=" * 70)
    print("🎬 SIMULATION DE DÉMONSTRATION - Système de Paris Sportifs")
    print("=" * 70)
    
    # Étape 1: Créer l'historique de démonstration
    tracker = create_demo_history()
    
    # Étape 2: Ajouter les paris réels d'aujourd'hui
    tracker = add_todays_pending_bets()
    
    # Étape 3: Afficher les statistiques finales
    stats = tracker.get_statistics()
    league_stats = tracker.get_league_statistics()
    
    print(f"\n" + "="*70)
    print("📊 STATISTIQUES FINALES DE LA DÉMONSTRATION")
    print("="*70)
    
    print(f"💰 Bankroll: {stats['current_bankroll']:.2f}€ (départ: 1000€)")
    print(f"📈 Profit/Perte: {stats['profit_loss']:+.2f}€")
    print(f"🎯 Taux de réussite: {stats['win_rate']:.1f}% ({stats['winning_bets']}/{stats['total_bets']})")
    print(f"📊 ROI: {stats['roi_percentage']:+.1f}%")
    print(f"⏳ Paris en attente: {stats['pending_bets']}")
    
    if not league_stats.empty:
        print(f"\n🏆 TOP 5 LIGUES PAR ROI:")
        for i, (_, league) in enumerate(league_stats.head().iterrows(), 1):
            print(f"   {i}. {league['league']}: {league['total_roi']:+.2f}€ ({league['win_rate']:.1f}% sur {league['total_bets']} paris)")
    
    print(f"\n🖥️ DASHBOARD DISPONIBLE:")
    print(f"   http://localhost:8501")
    print(f"   Explorez les 5 sections du dashboard pour voir:")
    print(f"   • 📊 Vue d'ensemble avec métriques")
    print(f"   • 💰 Paris du jour avec prédictions LSTM")
    print(f"   • 📈 Historique complet et graphiques")
    print(f"   • 🏆 Statistiques détaillées par ligues")
    print(f"   • ⚙️ Configuration et gestion")
    
    print(f"\n" + "="*70)

if __name__ == "__main__":
    main()