#!/usr/bin/env python3
# daily_betting_pipeline.py
# ---------------------------------------------------------------------------
# Pipeline quotidien automatisé pour la mise à jour des paris et résultats
# ---------------------------------------------------------------------------

import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from betting_tracker import BettingTracker

def run_command(command, description):
    """Exécute une commande avec logging"""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            return True
        else:
            print(f"❌ {description} - Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def main():
    """Pipeline quotidien principal"""
    print("=" * 70)
    print("🏈 PIPELINE QUOTIDIEN - Gestion Automatique des Paris")
    print("=" * 70)
    print(f"Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tracker = BettingTracker()
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # ==========================================
    # ÉTAPE 1: Mise à jour des résultats d'hier
    # ==========================================
    print(f"\n🔄 ÉTAPE 1: Mise à jour des résultats du {yesterday}")
    
    # Vérifier s'il y a des paris d'hier à mettre à jour
    history_df = tracker.get_history()
    if not history_df.empty:
        pending_yesterday = history_df[
            (history_df['date'] == yesterday) & (history_df['status'] == 'pending')
        ]
        
        if not pending_yesterday.empty:
            print(f"📊 {len(pending_yesterday)} paris en attente pour {yesterday}")
            tracker.update_results(yesterday)
        else:
            print(f"ℹ️ Aucun pari en attente pour {yesterday}")
    else:
        print("ℹ️ Aucun historique de paris")
    
    # ==========================================
    # ÉTAPE 2: Exécution du pipeline d'analyse
    # ==========================================
    print(f"\n📈 ÉTAPE 2: Analyse des matchs du {today}")
    
    pipeline_success = True
    pipeline_steps = [
        ("python ingestion/fetch_fixtures.py", "Récupération fixtures"),
        ("python ingestion/fetch_odds_api_football.py", "Récupération cotes"),
        ("python ingestion/merge_dataset.py", "Fusion datasets"),
        ("python preprocessing/create_lstm_sequences_fixed.py", "Séquences LSTM"),
        ("python modeling/lstm_model_fixed.py", "Modèle LSTM"),
        ("python analyse_bets_fixed.py", "Analyse value bets"),
    ]
    
    for command, description in pipeline_steps:
        if not run_command(command, description):
            pipeline_success = False
            print(f"⚠️ Arrêt du pipeline à cause d'une erreur dans: {description}")
            break
    
    # ==========================================
    # ÉTAPE 3: Ajout des nouveaux paris
    # ==========================================
    if pipeline_success:
        print(f"\n💰 ÉTAPE 3: Gestion des paris du {today}")
        
        # Vérifier si on a des value bets aujourd'hui
        if os.path.exists("data/bets_today.csv"):
            import pandas as pd
            bets_df = pd.read_csv("data/bets_today.csv")
            
            if not bets_df.empty:
                print(f"💎 {len(bets_df)} value bets détectés aujourd'hui")
                
                # Demander si on veut ajouter automatiquement
                auto_add = input(f"🤖 Ajouter automatiquement ces {len(bets_df)} paris à l'historique ? (y/n): ").lower().strip()
                
                if auto_add in ['y', 'yes', 'oui', 'o']:
                    # Demander le multiplicateur de mise
                    try:
                        multiplier = float(input("💵 Multiplicateur de mise (défaut 1.0): ") or "1.0")
                    except ValueError:
                        multiplier = 1.0
                    
                    tracker.add_todays_bets(multiplier)
                    print("✅ Paris ajoutés à l'historique!")
                else:
                    print("ℹ️ Paris non ajoutés - vous pouvez les ajouter manuellement via le dashboard")
            else:
                print("ℹ️ Aucun value bet détecté aujourd'hui")
        else:
            print("⚠️ Aucun fichier de paris trouvé")
    
    # ==========================================
    # ÉTAPE 4: Rapport de synthèse
    # ==========================================
    print(f"\n📊 ÉTAPE 4: Rapport de synthèse")
    
    # Statistiques actuelles
    stats = tracker.get_statistics()
    config = tracker.get_config()
    
    print("\n" + "="*50)
    print("📈 RAPPORT QUOTIDIEN")
    print("="*50)
    
    print(f"💰 Bankroll actuel: {stats['current_bankroll']:.2f}€")
    print(f"📈 Profit/Perte total: {stats['profit_loss']:+.2f}€")
    print(f"🎯 Taux de réussite: {stats['win_rate']:.1f}% ({stats['winning_bets']}/{stats['total_bets']})")
    print(f"📊 ROI: {stats['roi_percentage']:+.1f}%")
    print(f"⏳ Paris en attente: {stats['pending_bets']}")
    
    # Performance des 7 derniers jours
    if not history_df.empty:
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        recent_completed = history_df[
            (history_df['date'] >= week_ago) & (history_df['status'] == 'completed')
        ]
        
        if not recent_completed.empty:
            week_profit = recent_completed['profit_loss'].sum()
            week_bets = len(recent_completed)
            week_wins = len(recent_completed[recent_completed['won'] == True])
            week_winrate = (week_wins / week_bets * 100) if week_bets > 0 else 0
            
            print(f"\n📅 Performance 7 derniers jours:")
            print(f"   💎 Profit: {week_profit:+.2f}€")
            print(f"   🎲 Paris: {week_bets} ({week_wins} gagnants)")
            print(f"   🎯 Taux: {week_winrate:.1f}%")
    
    # Conseils automatiques
    print(f"\n🎯 Conseils:")
    if stats['win_rate'] > 55:
        print("   ✅ Excellent taux de réussite! Continuez cette stratégie.")
    elif stats['win_rate'] > 45:
        print("   📊 Taux de réussite correct. Surveillez les value bets.")
    else:
        print("   ⚠️ Taux de réussite faible. Révisez les critères de sélection.")
    
    if stats['roi_percentage'] > 10:
        print("   💰 ROI très positif! Excellente performance.")
    elif stats['roi_percentage'] > 0:
        print("   📈 ROI positif. Bonne direction.")
    else:
        print("   📉 ROI négatif. Attention aux mises et sélections.")
    
    # Informations sur le dashboard
    print(f"\n🖥️ Dashboard disponible:")
    print(f"   streamlit run dashboard/enhanced_streamlit_app.py --server.port=8501")
    
    print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

if __name__ == "__main__":
    main()