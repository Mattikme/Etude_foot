#!/usr/bin/env python3
# run_complete_pipeline.py
# ---------------------------------------------------------------------------
# Pipeline complet corrigé pour l'analyse des paris sportifs
# Exécute toutes les étapes dans le bon ordre avec gestion d'erreurs
# ---------------------------------------------------------------------------

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description, required=True):
    """
    Exécute une commande avec gestion d'erreurs et logging
    """
    print(f"\n🚀 {description}...")
    print(f"Commande: {command}")
    
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - Succès ({duration:.1f}s)")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Échec (code {result.returncode})")
            if result.stderr.strip():
                print(f"Erreur: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            if required:
                print("⚠️ Étape critique échouée, arrêt du pipeline")
                return False
            return True
            
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        if required:
            return False
        return True

def check_file_exists(filepath, description):
    """Vérifie qu'un fichier critique existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} manquant: {filepath}")
        return False

def main():
    """Pipeline principal"""
    print("=" * 70)
    print("🏈 FOOTBALL LSTM PREDICTOR - Pipeline Complet")
    print("=" * 70)
    print(f"Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérifier les prérequis
    print(f"\n📋 Vérification des prérequis...")
    
    required_configs = [
        ("config/api_keys.yaml", "Configuration API"),
        ("config/target_league_ids.yaml", "IDs des ligues")
    ]
    
    for filepath, desc in required_configs:
        if not check_file_exists(filepath, desc):
            print("❌ Configuration manquante, arrêt du pipeline")
            return
    
    # Créer les dossiers nécessaires
    print(f"\n📁 Création des dossiers...")
    directories = ["data/raw", "data/processed", "data/lstm"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Dossier: {directory}")
    
    # Pipeline d'exécution
    pipeline_steps = [
        # Étape 1: Ingestion des données
        ("python ingestion/fetch_fixtures.py", "Récupération des fixtures", True),
        ("python ingestion/fetch_standings.py", "Récupération des standings", True), 
        ("python ingestion/fetch_odds_api_football.py", "Récupération des cotes", True),
        
        # Étape 2: Preprocessing  
        ("python generate_rankings_from_standings.py", "Génération des rankings", True),
        ("python ingestion/merge_dataset.py", "Fusion des datasets", True),
        ("python preprocessing/create_lstm_sequences_fixed.py", "Création séquences LSTM", True),
        
        # Étape 3: Modélisation
        ("python modeling/lstm_model_fixed.py", "Entraînement modèle LSTM", True),
        
        # Étape 4: Analyse
        ("python analyse_bets_fixed.py", "Analyse des value bets", True),
    ]
    
    # Exécution du pipeline
    success_count = 0
    for i, (command, description, required) in enumerate(pipeline_steps, 1):
        print(f"\n{'='*50}")
        print(f"ÉTAPE {i}/{len(pipeline_steps)}: {description}")
        print(f"{'='*50}")
        
        if run_command(command, description, required):
            success_count += 1
        else:
            print("❌ Pipeline interrompu à cause d'une erreur critique")
            return
    
    # Vérification des fichiers de sortie
    print(f"\n{'='*50}")
    print("VÉRIFICATION DES RÉSULTATS")
    print(f"{'='*50}")
    
    output_files = [
        ("data/rankings.csv", "Rankings des équipes"),
        ("data/processed/base_matches.csv", "Matches du jour"),
        ("data/lstm/predictions_today.csv", "Prédictions LSTM"),
        ("data/bets_today.csv", "Value bets détectés")
    ]
    
    files_ok = 0
    for filepath, description in output_files:
        if check_file_exists(filepath, description):
            files_ok += 1
            # Afficher quelques statistiques
            try:
                if filepath.endswith('.csv'):
                    import pandas as pd
                    df = pd.read_csv(filepath)
                    print(f"    📊 {len(df)} lignes dans le fichier")
            except:
                pass
    
    # Résumé final
    print(f"\n{'='*70}")
    print("📊 RÉSUMÉ D'EXÉCUTION")
    print(f"{'='*70}")
    print(f"✅ Étapes réussies: {success_count}/{len(pipeline_steps)}")
    print(f"✅ Fichiers générés: {files_ok}/{len(output_files)}")
    
    if success_count == len(pipeline_steps) and files_ok == len(output_files):
        print("\n🎉 PIPELINE COMPLET RÉUSSI ! 🎉")
        print("\n📈 Dashboard disponible:")
        print("   streamlit run dashboard/streamlit_app_fixed.py --server.port=8501")
        print("\n📁 Fichiers générés:")
        for filepath, description in output_files:
            print(f"   - {filepath}")
    else:
        print(f"\n⚠️ Pipeline partiellement réussi ({success_count}/{len(pipeline_steps)} étapes)")
    
    print(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()