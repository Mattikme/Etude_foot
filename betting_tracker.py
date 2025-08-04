#!/usr/bin/env python3
# betting_tracker.py
# ---------------------------------------------------------------------------
# Système de suivi des paris avec historique automatique et bankroll virtuel
# ---------------------------------------------------------------------------

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from glob import glob

class BettingTracker:
    def __init__(self, initial_bankroll=1000, default_bet_size=10):
        """
        Initialise le tracker de paris
        
        Args:
            initial_bankroll (float): Bankroll initial en €
            default_bet_size (float): Mise par défaut en €
        """
        self.initial_bankroll = initial_bankroll
        self.default_bet_size = default_bet_size
        self.history_file = "data/betting_history.csv"
        self.config_file = "data/betting_config.json"
        
        # Créer les fichiers s'ils n'existent pas
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialise les fichiers de configuration et d'historique"""
        os.makedirs("data", exist_ok=True)
        
        # Configuration
        if not os.path.exists(self.config_file):
            config = {
                "initial_bankroll": self.initial_bankroll,
                "current_bankroll": self.initial_bankroll,
                "default_bet_size": self.default_bet_size,
                "total_bets": 0,
                "winning_bets": 0,
                "total_roi": 0.0,
                "last_update": datetime.now().isoformat()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Historique
        if not os.path.exists(self.history_file):
            history_df = pd.DataFrame(columns=[
                'date', 'match', 'league', 'bet_on', 'odds', 'bet_amount', 
                'predicted_prob', 'expected_value', 'status', 'actual_result', 
                'won', 'profit_loss', 'bankroll_after'
            ])
            history_df.to_csv(self.history_file, index=False)
    
    def get_config(self):
        """Charge la configuration actuelle"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config):
        """Sauvegarde la configuration"""
        config["last_update"] = datetime.now().isoformat()
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def add_todays_bets(self, bet_size_multiplier=1.0):
        """
        Ajoute les paris d'aujourd'hui à l'historique
        
        Args:
            bet_size_multiplier (float): Multiplicateur de mise (1.0 = mise normale)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Vérifier si les paris d'aujourd'hui sont déjà ajoutés
        if os.path.exists(self.history_file):
            history_df = pd.read_csv(self.history_file)
            if not history_df.empty and today in history_df['date'].values:
                print(f"⚠️ Les paris du {today} sont déjà dans l'historique")
                return
        
        # Charger les value bets d'aujourd'hui
        bets_file = "data/bets_today.csv"
        if not os.path.exists(bets_file):
            print(f"❌ Aucun pari trouvé pour aujourd'hui : {bets_file}")
            return
        
        bets_df = pd.read_csv(bets_file)
        if bets_df.empty:
            print(f"⚠️ Aucun value bet détecté aujourd'hui")
            return
        
        # Charger les matchs pour récupérer les ligues
        matches_file = "data/processed/base_matches.csv"
        matches_df = pd.read_csv(matches_file) if os.path.exists(matches_file) else pd.DataFrame()
        
        # Mapper les matchs aux ligues
        league_mapping = {}
        if not matches_df.empty and 'league.name' in matches_df.columns:
            for _, match in matches_df.iterrows():
                home_team = match.get('teams.home.name', '')
                away_team = match.get('teams.away.name', '')
                if home_team and away_team:
                    match_name = f"{home_team} vs {away_team}"
                    league_mapping[match_name] = match.get('league.name', 'Inconnue')
        
        config = self.get_config()
        current_bankroll = config['current_bankroll']
        
        new_bets = []
        
        for _, bet in bets_df.iterrows():
            bet_amount = self.default_bet_size * bet_size_multiplier
            league = league_mapping.get(bet['match'], 'Inconnue')
            
            new_bet = {
                'date': today,
                'match': bet['match'],
                'league': league,
                'bet_on': bet['bet_on'],
                'odds': bet['bookmaker_odds'],
                'bet_amount': bet_amount,
                'predicted_prob': bet['expected_prob'],
                'expected_value': bet['expected_value'],
                'status': 'pending',
                'actual_result': '',
                'won': False,
                'profit_loss': 0.0,
                'bankroll_after': current_bankroll
            }
            new_bets.append(new_bet)
        
        # Ajouter à l'historique
        if os.path.exists(self.history_file):
            history_df = pd.read_csv(self.history_file)
            new_bets_df = pd.DataFrame(new_bets)
            history_df = pd.concat([history_df, new_bets_df], ignore_index=True)
        else:
            history_df = pd.DataFrame(new_bets)
        
        history_df.to_csv(self.history_file, index=False)
        
        # Mettre à jour la configuration
        config['total_bets'] += len(new_bets)
        self.save_config(config)
        
        print(f"✅ {len(new_bets)} paris ajoutés à l'historique pour le {today}")
    
    def update_results(self, date=None):
        """
        Met à jour les résultats des paris d'une date donnée
        
        Args:
            date (str): Date au format YYYY-MM-DD (par défaut = hier)
        """
        if date is None:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Charger l'historique
        if not os.path.exists(self.history_file):
            print("❌ Aucun historique de paris trouvé")
            return
        
        history_df = pd.read_csv(self.history_file)
        pending_bets = history_df[
            (history_df['date'] == date) & (history_df['status'] == 'pending')
        ]
        
        if pending_bets.empty:
            print(f"ℹ️ Aucun pari en attente pour le {date}")
            return
        
        # Charger les résultats des matchs
        fixtures_files = glob(f"data/raw/fixtures_*_{date}.json")
        match_results = {}
        
        for fixtures_file in fixtures_files:
            try:
                with open(fixtures_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for match in data.get('response', []):
                    home_team = match.get('teams', {}).get('home', {}).get('name')
                    away_team = match.get('teams', {}).get('away', {}).get('name')
                    goals_home = match.get('goals', {}).get('home')
                    goals_away = match.get('goals', {}).get('away')
                    status = match.get('fixture', {}).get('status', {}).get('short')
                    
                    if home_team and away_team and goals_home is not None and goals_away is not None and status == 'FT':
                        match_name = f"{home_team} vs {away_team}"
                        
                        if goals_home > goals_away:
                            result = "Home"
                        elif goals_away > goals_home:
                            result = "Away"
                        else:
                            result = "Draw"
                        
                        match_results[match_name] = result
                        
            except Exception as e:
                print(f"⚠️ Erreur lecture résultats {fixtures_file}: {e}")
                continue
        
        # Mettre à jour les paris
        updated_count = 0
        config = self.get_config()
        
        for idx, bet in pending_bets.iterrows():
            match_name = bet['match']
            
            if match_name in match_results:
                actual_result = match_results[match_name]
                won = actual_result == bet['bet_on']
                
                if won:
                    profit_loss = bet['bet_amount'] * (bet['odds'] - 1)
                else:
                    profit_loss = -bet['bet_amount']
                
                # Mettre à jour l'historique
                history_df.loc[idx, 'status'] = 'completed'
                history_df.loc[idx, 'actual_result'] = actual_result
                history_df.loc[idx, 'won'] = won
                history_df.loc[idx, 'profit_loss'] = profit_loss
                
                # Mettre à jour bankroll
                new_bankroll = config['current_bankroll'] + profit_loss
                history_df.loc[idx, 'bankroll_after'] = new_bankroll
                config['current_bankroll'] = new_bankroll
                
                if won:
                    config['winning_bets'] += 1
                
                config['total_roi'] += profit_loss
                updated_count += 1
        
        # Sauvegarder
        history_df.to_csv(self.history_file, index=False)
        self.save_config(config)
        
        print(f"✅ {updated_count} paris mis à jour pour le {date}")
        print(f"💰 Bankroll actuel: {config['current_bankroll']:.2f}€")
    
    def get_history(self):
        """Retourne l'historique complet des paris"""
        if os.path.exists(self.history_file):
            return pd.read_csv(self.history_file)
        return pd.DataFrame()
    
    def get_statistics(self):
        """Calcule les statistiques globales"""
        config = self.get_config()
        history_df = self.get_history()
        
        if history_df.empty:
            return {
                'total_bets': 0,
                'winning_bets': 0,
                'win_rate': 0,
                'total_roi': 0,
                'roi_percentage': 0,
                'current_bankroll': config['current_bankroll'],
                'profit_loss': 0,
                'avg_odds': 0,
                'pending_bets': 0
            }
        
        completed_bets = history_df[history_df['status'] == 'completed']
        
        stats = {
            'total_bets': len(completed_bets),
            'winning_bets': len(completed_bets[completed_bets['won'] == True]),
            'win_rate': len(completed_bets[completed_bets['won'] == True]) / len(completed_bets) * 100 if len(completed_bets) > 0 else 0,
            'total_roi': completed_bets['profit_loss'].sum(),
            'roi_percentage': (completed_bets['profit_loss'].sum() / config['initial_bankroll']) * 100,
            'current_bankroll': config['current_bankroll'],
            'profit_loss': config['current_bankroll'] - config['initial_bankroll'],
            'avg_odds': completed_bets['odds'].mean() if len(completed_bets) > 0 else 0,
            'pending_bets': len(history_df[history_df['status'] == 'pending'])
        }
        
        return stats
    
    def get_league_statistics(self):
        """Calcule les statistiques par ligue"""
        history_df = self.get_history()
        completed_bets = history_df[history_df['status'] == 'completed']
        
        if completed_bets.empty:
            return pd.DataFrame()
        
        league_stats = []
        
        for league in completed_bets['league'].unique():
            league_bets = completed_bets[completed_bets['league'] == league]
            
            stats = {
                'league': league,
                'total_bets': len(league_bets),
                'winning_bets': len(league_bets[league_bets['won'] == True]),
                'win_rate': len(league_bets[league_bets['won'] == True]) / len(league_bets) * 100,
                'total_roi': league_bets['profit_loss'].sum(),
                'avg_odds': league_bets['odds'].mean(),
                'avg_expected_value': league_bets['expected_value'].mean()
            }
            league_stats.append(stats)
        
        return pd.DataFrame(league_stats).sort_values('total_roi', ascending=False)

def main():
    """Fonction principale pour tests"""
    tracker = BettingTracker()
    
    # Ajouter les paris d'aujourd'hui
    tracker.add_todays_bets()
    
    # Mettre à jour les résultats d'hier
    tracker.update_results()
    
    # Afficher les statistiques
    stats = tracker.get_statistics()
    print("\n📊 Statistiques globales:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    main()