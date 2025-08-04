#!/usr/bin/env python3
# dashboard/streamlit_app_fixed.py
# ---------------------------------------------------------------------------
# Dashboard Streamlit pour visualiser les prédictions LSTM et value bets
# ---------------------------------------------------------------------------

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="📊 Football LSTM Predictor",
    page_icon="⚽",
    layout="wide"
)

# Titre principal
st.title("📊 Analyse des Paris Sportifs - Modèle LSTM + Value Bets")
st.markdown("---")

# Sidebar avec informations générales
st.sidebar.header("🔧 Informations Système")
today = datetime.today().strftime("%Y-%m-%d")
st.sidebar.info(f"Date d'analyse: {today}")

# Vérification des fichiers nécessaires
required_files = {
    "Prédictions LSTM": "data/lstm/predictions_today.csv",
    "Value Bets": "data/bets_today.csv", 
    "Rankings": "data/rankings.csv",
    "Matchs du jour": "data/processed/base_matches.csv"
}

files_status = {}
for name, filepath in required_files.items():
    files_status[name] = "✅" if os.path.exists(filepath) else "❌"
    st.sidebar.write(f"{files_status[name]} {name}")

# Section 1: Prédictions LSTM
st.header("🎯 Prédictions LSTM du jour")

try:
    if os.path.exists("data/lstm/predictions_today.csv"):
        predictions_df = pd.read_csv("data/lstm/predictions_today.csv")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Matchs", len(predictions_df))
        with col2:
            avg_confidence = predictions_df["confidence"].mean()
            st.metric("Confiance Moyenne", f"{avg_confidence:.1%}")
        with col3:
            home_wins = len(predictions_df[predictions_df["predicted_outcome"] == "Home"])
            st.metric("Victoires Domicile Prédites", f"{home_wins}/{len(predictions_df)}")
        
        # Graphique de distribution des probabilités
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Distribution des probabilités par outcome
        outcomes = predictions_df["predicted_outcome"].value_counts()
        ax1.pie(outcomes.values, labels=outcomes.index, autopct='%1.1f%%', startangle=90)
        ax1.set_title("Distribution des Prédictions")
        
        # Histogram de la confiance
        ax2.hist(predictions_df["confidence"], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
        ax2.set_xlabel("Niveau de Confiance")
        ax2.set_ylabel("Nombre de Matchs")
        ax2.set_title("Distribution de la Confiance")
        ax2.axvline(avg_confidence, color='red', linestyle='--', label=f'Moyenne: {avg_confidence:.1%}')
        ax2.legend()
        
        st.pyplot(fig)
        
        # Tableau des prédictions
        st.subheader("📋 Détail des Prédictions")
        display_df = predictions_df[["match", "predicted_outcome", "confidence", "prob_home", "prob_draw", "prob_away"]].copy()
        display_df["prob_home"] = display_df["prob_home"].apply(lambda x: f"{x:.1%}")
        display_df["prob_draw"] = display_df["prob_draw"].apply(lambda x: f"{x:.1%}")
        display_df["prob_away"] = display_df["prob_away"].apply(lambda x: f"{x:.1%}")
        display_df["confidence"] = display_df["confidence"].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.error("❌ Fichier des prédictions LSTM non trouvé")
        
except Exception as e:
    st.error(f"❌ Erreur chargement prédictions: {e}")

st.markdown("---")

# Section 2: Value Bets
st.header("💰 Value Bets Détectés")

try:
    if os.path.exists("data/bets_today.csv"):
        bets_df = pd.read_csv("data/bets_today.csv")
        
        if not bets_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Value Bets", len(bets_df))
            with col2:
                total_value = bets_df["expected_value"].sum()
                st.metric("Value Cumulé", f"+{total_value:.1%}")
            with col3:
                avg_odds = bets_df["bookmaker_odds"].mean()
                st.metric("Cote Moyenne", f"{avg_odds:.2f}")
            with col4:
                avg_edge = bets_df["edge"].mean()
                st.metric("Edge Moyen", f"+{avg_edge:.1f}%")
            
            # Graphique des value bets
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Top 10 value bets
            top_bets = bets_df.head(10)
            ax1.barh(range(len(top_bets)), top_bets["expected_value"], color='green', alpha=0.7)
            ax1.set_yticks(range(len(top_bets)))
            ax1.set_yticklabels([f"{row['match'][:20]}... ({row['bet_on']})" for _, row in top_bets.iterrows()])
            ax1.set_xlabel("Expected Value")
            ax1.set_title("Top 10 Value Bets")
            ax1.grid(axis='x', alpha=0.3)
            
            # Distribution par type de pari
            bet_types = bets_df["bet_on"].value_counts()
            ax2.bar(bet_types.index, bet_types.values, color=['lightblue', 'lightgreen', 'lightcoral'])
            ax2.set_xlabel("Type de Pari")
            ax2.set_ylabel("Nombre")
            ax2.set_title("Distribution par Type de Pari")
            
            st.pyplot(fig)
            
            # Tableau des value bets
            st.subheader("🏆 Top Value Bets")
            display_bets = bets_df[["match", "bet_on", "bookmaker_odds", "expected_prob", "expected_value", "edge"]].copy()
            display_bets["expected_prob"] = display_bets["expected_prob"].apply(lambda x: f"{x:.1%}")
            display_bets["expected_value"] = display_bets["expected_value"].apply(lambda x: f"+{x:.1%}")
            display_bets["edge"] = display_bets["edge"].apply(lambda x: f"+{x:.1f}%")
            
            st.dataframe(display_bets, use_container_width=True)
            
        else:
            st.info("ℹ️ Aucun value bet détecté aujourd'hui")
            
    else:
        st.error("❌ Fichier des value bets non trouvé")
        
except Exception as e:
    st.error(f"❌ Erreur chargement value bets: {e}")

st.markdown("---")

# Section 3: Statistiques générales
st.header("📈 Statistiques Générales")

try:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏟️ Matchs Analysés")
        if os.path.exists("data/processed/base_matches.csv"):
            matches_df = pd.read_csv("data/processed/base_matches.csv")
            
            # Grouper par ligue
            if "league.name" in matches_df.columns:
                league_counts = matches_df["league.name"].value_counts().head(10)
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.bar(range(len(league_counts)), league_counts.values, color='steelblue', alpha=0.8)
                ax.set_xticks(range(len(league_counts)))
                ax.set_xticklabels(league_counts.index, rotation=45, ha='right')
                ax.set_ylabel("Nombre de Matchs")
                ax.set_title("Matchs par Ligue")
                ax.grid(axis='y', alpha=0.3)
                st.pyplot(fig)
            else:
                st.write(f"Total matchs analysés: {len(matches_df)}")
        else:
            st.error("❌ Données de matchs non disponibles")
    
    with col2:
        st.subheader("🏆 Top Rankings")
        if os.path.exists("data/rankings.csv"):
            rankings_df = pd.read_csv("data/rankings.csv")
            top_rankings = rankings_df.head(15)
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.barh(range(len(top_rankings)), top_rankings["ranking"], color='gold', alpha=0.8)
            ax.set_yticks(range(len(top_rankings)))
            ax.set_yticklabels([team[:20] + ('...' if len(team) > 20 else '') for team in top_rankings["team"]])
            ax.set_xlabel("Score de Ranking")
            ax.set_title("Top 15 Équipes")
            ax.grid(axis='x', alpha=0.3)
            st.pyplot(fig)
        else:
            st.error("❌ Données de rankings non disponibles")
            
except Exception as e:
    st.error(f"❌ Erreur statistiques générales: {e}")

# Footer
st.markdown("---")
st.markdown("### 🔧 À propos")
st.info("""
**Football LSTM Predictor** utilise un modèle LSTM entraîné sur des données historiques 
pour prédire les résultats de matchs et identifier les value bets. 

**Fonctionnalités:**
- 🤖 Modèle LSTM pour prédictions
- 📊 Analyse des cotes en temps réel  
- 💰 Détection automatique des value bets
- 📈 Dashboard interactif

**Sources de données:** API-Football via RapidAPI
""")

# Affichage de debug si nécessaire
if st.sidebar.checkbox("🐛 Mode Debug"):
    st.markdown("---")
    st.header("🐛 Informations Debug")
    
    for name, filepath in required_files.items():
        if os.path.exists(filepath):
            try:
                if filepath.endswith('.csv'):
                    df = pd.read_csv(filepath)
                    st.write(f"**{name}**: {len(df)} lignes, {len(df.columns)} colonnes")
                    with st.expander(f"Aperçu {name}"):
                        st.dataframe(df.head(3))
            except Exception as e:
                st.write(f"**{name}**: Erreur - {e}")
        else:
            st.write(f"**{name}**: ❌ Fichier manquant")