#!/usr/bin/env python3
# dashboard/enhanced_streamlit_app.py
# ---------------------------------------------------------------------------
# Dashboard Streamlit complet avec historique, bankroll virtuel et stats par ligues
# ---------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from glob import glob
import sys
import os

# Ajouter le répertoire parent au path pour imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from betting_tracker import BettingTracker

# Configuration de la page
st.set_page_config(
    page_title="🏈 Football Betting Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    color: #1f77b4;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.positive { color: #28a745; }
.negative { color: #dc3545; }
.neutral { color: #6c757d; }
</style>
""", unsafe_allow_html=True)

# Initialiser le tracker
@st.cache_data
def init_tracker():
    return BettingTracker()

def load_todays_bets():
    """Charge les paris du jour"""
    if os.path.exists("data/bets_today.csv"):
        return pd.read_csv("data/bets_today.csv")
    return pd.DataFrame()

def load_todays_predictions():
    """Charge les prédictions du jour"""
    if os.path.exists("data/lstm/predictions_today.csv"):
        return pd.read_csv("data/lstm/predictions_today.csv")
    return pd.DataFrame()

# Sidebar avec navigation
st.sidebar.title("🎯 Navigation")
page = st.sidebar.selectbox(
    "Choisir une page",
    ["📊 Dashboard Principal", "💰 Paris du Jour", "📈 Historique & Stats", "🏆 Stats par Ligues", "⚙️ Configuration"]
)

# Titre principal
st.markdown('<h1 class="main-header">🏈 Football LSTM Betting Dashboard</h1>', unsafe_allow_html=True)

# Initialisation
tracker = BettingTracker()
today = datetime.now().strftime("%Y-%m-%d")

# ========================
# PAGE 1: DASHBOARD PRINCIPAL
# ========================
if page == "📊 Dashboard Principal":
    st.header("📊 Vue d'ensemble")
    
    # Métriques principales
    stats = tracker.get_statistics()
    config = tracker.get_config()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        profit_class = "positive" if stats['profit_loss'] > 0 else "negative" if stats['profit_loss'] < 0 else "neutral"
        st.metric(
            "💰 Bankroll", 
            f"{stats['current_bankroll']:.2f}€",
            f"{stats['profit_loss']:+.2f}€"
        )
    
    with col2:
        st.metric(
            "🎯 Taux de réussite",
            f"{stats['win_rate']:.1f}%",
            f"{stats['winning_bets']}/{stats['total_bets']}"
        )
    
    with col3:
        roi_class = "positive" if stats['roi_percentage'] > 0 else "negative" if stats['roi_percentage'] < 0 else "neutral"
        st.metric(
            "📈 ROI",
            f"{stats['roi_percentage']:+.1f}%",
            f"{stats['total_roi']:+.2f}€"
        )
    
    with col4:
        st.metric(
            "🎲 Paris en attente",
            stats['pending_bets'],
            f"Cote moy: {stats['avg_odds']:.2f}" if stats['avg_odds'] > 0 else ""
        )
    
    with col5:
        st.metric(
            "📅 Dernière MAJ",
            config['last_update'][:10],
            ""
        )
    
    st.markdown("---")
    
    # Graphiques de vue d'ensemble
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Évolution du Bankroll")
        history_df = tracker.get_history()
        
        if not history_df.empty and 'bankroll_after' in history_df.columns:
            # Créer une série temporelle du bankroll
            bankroll_evolution = []
            dates = []
            current_bankroll = config['initial_bankroll']
            
            for date in sorted(history_df['date'].unique()):
                day_bets = history_df[history_df['date'] == date]
                completed_bets = day_bets[day_bets['status'] == 'completed']
                
                if not completed_bets.empty:
                    day_profit = completed_bets['profit_loss'].sum()
                    current_bankroll += day_profit
                
                bankroll_evolution.append(current_bankroll)
                dates.append(date)
            
            if dates:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, y=bankroll_evolution,
                    mode='lines+markers',
                    name='Bankroll',
                    line=dict(color='#1f77b4', width=3),
                    fill='tonexty'
                ))
                fig.add_hline(
                    y=config['initial_bankroll'], 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text="Bankroll Initial"
                )
                fig.update_layout(
                    title="Évolution du Bankroll dans le Temps",
                    xaxis_title="Date",
                    yaxis_title="Bankroll (€)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("🔄 Pas encore de données d'historique pour le graphique")
        else:
            st.info("📊 En attente de données pour l'évolution du bankroll")
    
    with col2:
        st.subheader("🎯 Répartition des Paris")
        
        todays_bets = load_todays_bets()
        if not todays_bets.empty:
            bet_types = todays_bets['bet_on'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=bet_types.index,
                values=bet_types.values,
                hole=.3,
                marker_colors=['#ff6b6b', '#4ecdc4', '#45b7d1']
            )])
            fig.update_layout(
                title="Répartition des Types de Paris (Aujourd'hui)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🎲 Aucun pari disponible pour aujourd'hui")

# ========================
# PAGE 2: PARIS DU JOUR
# ========================
elif page == "💰 Paris du Jour":
    st.header("💰 Paris du Jour")
    
    # Contrôles
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Actualiser les Paris", type="primary"):
            st.rerun()
    
    with col2:
        bet_multiplier = st.slider("💵 Multiplicateur de mise", 0.1, 5.0, 1.0, 0.1)
    
    with col3:
        if st.button("📝 Ajouter à l'Historique"):
            tracker.add_todays_bets(bet_multiplier)
            st.success("✅ Paris ajoutés à l'historique!")
            st.rerun()
    
    # Chargement des données
    todays_bets = load_todays_bets()
    predictions = load_todays_predictions()
    
    if not todays_bets.empty:
        st.subheader(f"🎯 {len(todays_bets)} Value Bets Détectés")
        
        # Métriques des paris du jour
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_value = todays_bets['expected_value'].sum()
            st.metric("💎 Value Totale", f"+{total_value:.1%}")
        
        with col2:
            avg_odds = todays_bets['bookmaker_odds'].mean()
            st.metric("🎲 Cote Moyenne", f"{avg_odds:.2f}")
        
        with col3:
            avg_edge = todays_bets['edge'].mean()
            st.metric("⚡ Edge Moyen", f"+{avg_edge:.1f}%")
        
        with col4:
            potential_profit = (todays_bets['bookmaker_odds'] * tracker.default_bet_size * bet_multiplier - tracker.default_bet_size * bet_multiplier).sum()
            st.metric("💰 Profit Potentiel", f"{potential_profit:.2f}€")
        
        # Tableau des paris avec mise calculée
        st.subheader("📋 Détail des Paris Recommandés")
        
        display_bets = todays_bets.copy()
        display_bets['mise_recommandee'] = tracker.default_bet_size * bet_multiplier
        display_bets['profit_potentiel'] = display_bets['mise_recommandee'] * (display_bets['bookmaker_odds'] - 1)
        
        # Formatage pour l'affichage
        display_columns = {
            'match': 'Match',
            'bet_on': 'Pari',
            'bookmaker_odds': 'Cote',
            'expected_prob': 'Prob. Prédite',
            'expected_value': 'Expected Value',
            'edge': 'Edge',
            'mise_recommandee': 'Mise Recommandée',
            'profit_potentiel': 'Profit Potentiel'
        }
        
        formatted_bets = display_bets[list(display_columns.keys())].copy()
        formatted_bets['expected_prob'] = formatted_bets['expected_prob'].apply(lambda x: f"{x:.1%}")
        formatted_bets['expected_value'] = formatted_bets['expected_value'].apply(lambda x: f"+{x:.1%}")
        formatted_bets['edge'] = formatted_bets['edge'].apply(lambda x: f"+{x:.1f}%")
        formatted_bets['mise_recommandee'] = formatted_bets['mise_recommandee'].apply(lambda x: f"{x:.2f}€")
        formatted_bets['profit_potentiel'] = formatted_bets['profit_potentiel'].apply(lambda x: f"+{x:.2f}€")
        
        formatted_bets.rename(columns=display_columns, inplace=True)
        
        st.dataframe(
            formatted_bets,
            use_container_width=True,
            hide_index=True
        )
        
        # Graphique des value bets
        st.subheader("📊 Visualisation des Value Bets")
        
        fig = px.bar(
            todays_bets.head(10),
            x='expected_value',
            y='match',
            color='bet_on',
            orientation='h',
            title="Top 10 Value Bets (Expected Value)",
            labels={'expected_value': 'Expected Value', 'match': 'Match'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("🔄 Aucun value bet détecté pour aujourd'hui. Lancez le pipeline d'analyse.")
    
    # Section Prédictions LSTM
    if not predictions.empty:
        st.markdown("---")
        st.subheader("🤖 Toutes les Prédictions LSTM")
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            confidence_filter = st.slider("🎯 Confiance minimale", 0.0, 1.0, 0.0, 0.05)
        with col2:
            outcome_filter = st.selectbox("🎲 Résultat prédit", ["Tous"] + list(predictions['predicted_outcome'].unique()))
        
        # Filtrer les prédictions
        filtered_preds = predictions.copy()
        if confidence_filter > 0:
            filtered_preds = filtered_preds[filtered_preds['confidence'] >= confidence_filter]
        if outcome_filter != "Tous":
            filtered_preds = filtered_preds[filtered_preds['predicted_outcome'] == outcome_filter]
        
        st.write(f"📊 {len(filtered_preds)} matchs affichés sur {len(predictions)} total")
        
        # Affichage des prédictions
        if not filtered_preds.empty:
            display_preds = filtered_preds[['match', 'predicted_outcome', 'confidence', 'prob_home', 'prob_draw', 'prob_away']].copy()
            display_preds['confidence'] = display_preds['confidence'].apply(lambda x: f"{x:.1%}")
            display_preds['prob_home'] = display_preds['prob_home'].apply(lambda x: f"{x:.1%}")
            display_preds['prob_draw'] = display_preds['prob_draw'].apply(lambda x: f"{x:.1%}")
            display_preds['prob_away'] = display_preds['prob_away'].apply(lambda x: f"{x:.1%}")
            
            display_preds.columns = ['Match', 'Prédiction', 'Confiance', 'Prob. Home', 'Prob. Draw', 'Prob. Away']
            
            st.dataframe(display_preds, use_container_width=True, hide_index=True)

# ========================
# PAGE 3: HISTORIQUE & STATS
# ========================
elif page == "📈 Historique & Stats":
    st.header("📈 Historique & Statistiques")
    
    # Contrôles de mise à jour
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Mettre à jour les résultats d'hier", type="primary"):
            tracker.update_results()
            st.success("✅ Résultats mis à jour!")
            st.rerun()
    
    with col2:
        update_date = st.date_input("📅 Mettre à jour une date spécifique")
        if st.button("📅 Mettre à jour cette date"):
            tracker.update_results(update_date.strftime("%Y-%m-%d"))
            st.success(f"✅ Résultats mis à jour pour le {update_date}!")
            st.rerun()
    
    with col3:
        st.write("") # Spacer
    
    # Statistiques globales détaillées
    stats = tracker.get_statistics()
    
    st.subheader("📊 Statistiques Globales")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 💰 Performance Financière")
        profit_color = "green" if stats['profit_loss'] > 0 else "red"
        st.markdown(f"""
        - **Bankroll Initial**: {tracker.get_config()['initial_bankroll']:.2f}€
        - **Bankroll Actuel**: {stats['current_bankroll']:.2f}€
        - **Profit/Perte**: <span style="color:{profit_color}">**{stats['profit_loss']:+.2f}€**</span>
        - **ROI**: <span style="color:{profit_color}">**{stats['roi_percentage']:+.1f}%**</span>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Performance des Paris")
        win_color = "green" if stats['win_rate'] > 50 else "orange" if stats['win_rate'] > 40 else "red"
        st.markdown(f"""
        - **Paris Totaux**: {stats['total_bets']}
        - **Paris Gagnants**: {stats['winning_bets']}
        - **Taux de Réussite**: <span style="color:{win_color}">**{stats['win_rate']:.1f}%**</span>
        - **Cote Moyenne**: {stats['avg_odds']:.2f}
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### ⏱️ État Actuel")
        st.markdown(f"""
        - **Paris en Attente**: {stats['pending_bets']}
        - **ROI Cumulé**: {stats['total_roi']:+.2f}€
        - **Dernière MAJ**: {tracker.get_config()['last_update'][:19]}
        """)
    
    # Historique complet
    history_df = tracker.get_history()
    
    if not history_df.empty:
        st.markdown("---")
        st.subheader("📋 Historique Complet des Paris")
        
        # Filtres pour l'historique
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox("📊 Statut", ["Tous", "completed", "pending"])
        with col2:
            league_filter = st.selectbox("🏆 Ligue", ["Toutes"] + sorted(history_df['league'].unique().tolist()))
        with col3:
            outcome_filter = st.selectbox("🎲 Type de pari", ["Tous", "Home", "Draw", "Away"])
        with col4:
            date_range = st.selectbox("📅 Période", ["Tous", "7 derniers jours", "30 derniers jours", "Cette semaine"])
        
        # Appliquer les filtres
        filtered_history = history_df.copy()
        
        if status_filter != "Tous":
            filtered_history = filtered_history[filtered_history['status'] == status_filter]
        if league_filter != "Toutes":
            filtered_history = filtered_history[filtered_history['league'] == league_filter]
        if outcome_filter != "Tous":
            filtered_history = filtered_history[filtered_history['bet_on'] == outcome_filter]
        
        if date_range != "Tous":
            today = datetime.now()
            if date_range == "7 derniers jours":
                start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
                filtered_history = filtered_history[filtered_history['date'] >= start_date]
            elif date_range == "30 derniers jours":
                start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
                filtered_history = filtered_history[filtered_history['date'] >= start_date]
        
        # Affichage de l'historique filtré
        st.write(f"📊 {len(filtered_history)} paris affichés sur {len(history_df)} total")
        
        if not filtered_history.empty:
            display_history = filtered_history[['date', 'match', 'league', 'bet_on', 'odds', 'bet_amount', 'status', 'won', 'profit_loss', 'bankroll_after']].copy()
            
            # Formatage
            display_history['bet_amount'] = display_history['bet_amount'].apply(lambda x: f"{x:.2f}€")
            display_history['profit_loss'] = display_history['profit_loss'].apply(lambda x: f"{x:+.2f}€")
            display_history['bankroll_after'] = display_history['bankroll_after'].apply(lambda x: f"{x:.2f}€")
            
            display_history.columns = ['Date', 'Match', 'Ligue', 'Pari', 'Cote', 'Mise', 'Statut', 'Gagné', 'P&L', 'Bankroll']
            
            st.dataframe(display_history, use_container_width=True, hide_index=True)
        
        # Graphiques d'analyse
        if len(filtered_history) > 1:
            st.markdown("---")
            st.subheader("📊 Analyses Graphiques")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Performance par jour
                if 'profit_loss' in filtered_history.columns:
                    daily_performance = filtered_history[filtered_history['status'] == 'completed'].groupby('date')['profit_loss'].sum().reset_index()
                    
                    if not daily_performance.empty:
                        fig = px.line(
                            daily_performance,
                            x='date', y='profit_loss',
                            title="Performance Quotidienne",
                            markers=True
                        )
                        fig.add_hline(y=0, line_dash="dash", line_color="red")
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Distribution des cotes
                completed_bets = filtered_history[filtered_history['status'] == 'completed']
                if not completed_bets.empty:
                    fig = px.histogram(
                        completed_bets,
                        x='odds',
                        color='won',
                        title="Distribution des Cotes par Résultat",
                        nbins=20
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📊 Aucun historique disponible. Ajoutez des paris pour voir les statistiques.")

# ========================
# PAGE 4: STATS PAR LIGUES
# ========================
elif page == "🏆 Stats par Ligues":
    st.header("🏆 Statistiques par Ligues")
    
    league_stats = tracker.get_league_statistics()
    
    if not league_stats.empty:
        st.subheader("📊 Performance par Ligue")
        
        # Métriques globales par ligues
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            best_league = league_stats.loc[league_stats['total_roi'].idxmax(), 'league']
            best_roi = league_stats['total_roi'].max()
            st.metric("🥇 Meilleure Ligue (ROI)", best_league, f"+{best_roi:.2f}€")
        
        with col2:
            best_winrate_idx = league_stats['win_rate'].idxmax()
            best_winrate_league = league_stats.loc[best_winrate_idx, 'league']
            best_winrate = league_stats.loc[best_winrate_idx, 'win_rate']
            st.metric("🎯 Meilleur Taux de Réussite", best_winrate_league, f"{best_winrate:.1f}%")
        
        with col3:
            most_active_idx = league_stats['total_bets'].idxmax()
            most_active_league = league_stats.loc[most_active_idx, 'league']
            most_active_bets = league_stats.loc[most_active_idx, 'total_bets']
            st.metric("🔥 Ligue la Plus Active", most_active_league, f"{most_active_bets} paris")
        
        with col4:
            total_leagues = len(league_stats)
            profitable_leagues = len(league_stats[league_stats['total_roi'] > 0])
            st.metric("📈 Ligues Profitables", f"{profitable_leagues}/{total_leagues}", f"{profitable_leagues/total_leagues*100:.0f}%")
        
        # Tableau détaillé des stats par ligue
        st.subheader("📋 Détail par Ligue")
        
        display_stats = league_stats.copy()
        display_stats = display_stats.round(2)
        
        # Formatage pour l'affichage
        display_stats['win_rate'] = display_stats['win_rate'].apply(lambda x: f"{x:.1f}%")
        display_stats['total_roi'] = display_stats['total_roi'].apply(lambda x: f"{x:+.2f}€")
        display_stats['avg_odds'] = display_stats['avg_odds'].apply(lambda x: f"{x:.2f}")
        display_stats['avg_expected_value'] = display_stats['avg_expected_value'].apply(lambda x: f"{x:.3f}")
        
        display_stats.columns = ['Ligue', 'Paris Totaux', 'Paris Gagnants', 'Taux de Réussite', 'ROI Total', 'Cote Moyenne', 'EV Moyen']
        
        st.dataframe(display_stats, use_container_width=True, hide_index=True)
        
        # Graphiques d'analyse par ligue
        st.markdown("---")
        st.subheader("📊 Analyses Visuelles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI par ligue
            fig = px.bar(
                league_stats.sort_values('total_roi', ascending=True).tail(15),
                x='total_roi', y='league',
                orientation='h',
                title="Top 15 Ligues par ROI",
                color='total_roi',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Scatter plot: Taux de réussite vs ROI
            fig = px.scatter(
                league_stats,
                x='win_rate', y='total_roi',
                size='total_bets',
                hover_name='league',
                title="Taux de Réussite vs ROI par Ligue",
                labels={'win_rate': 'Taux de Réussite (%)', 'total_roi': 'ROI Total (€)'}
            )
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            fig.add_vline(x=50, line_dash="dash", line_color="blue")
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap des performances
        st.subheader("🔥 Heatmap des Performances")
        
        # Préparer les données pour la heatmap
        history_df = tracker.get_history()
        completed_bets = history_df[history_df['status'] == 'completed'].copy()
        
        if not completed_bets.empty and 'date' in completed_bets.columns:
            # Créer une heatmap date x ligue
            completed_bets['date'] = pd.to_datetime(completed_bets['date'])
            completed_bets['week'] = completed_bets['date'].dt.isocalendar().week
            completed_bets['year_week'] = completed_bets['date'].dt.strftime('%Y-W%U')
            
            heatmap_data = completed_bets.pivot_table(
                values='profit_loss',
                index='league',
                columns='year_week',
                aggfunc='sum',
                fill_value=0
            )
            
            if not heatmap_data.empty:
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.heatmap(
                    heatmap_data,
                    annot=True,
                    fmt='.1f',
                    cmap='RdYlGn',
                    center=0,
                    ax=ax
                )
                ax.set_title("Profit/Perte par Ligue et Semaine (€)")
                ax.set_xlabel("Semaine")
                ax.set_ylabel("Ligue")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
    
    else:
        st.info("📊 Aucune donnée de ligue disponible. Complétez quelques paris pour voir les statistiques.")

# ========================
# PAGE 5: CONFIGURATION
# ========================
elif page == "⚙️ Configuration":
    st.header("⚙️ Configuration")
    
    config = tracker.get_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Paramètres de Bankroll")
        
        new_bankroll = st.number_input(
            "Bankroll Actuel (€)",
            min_value=0.0,
            value=float(config['current_bankroll']),
            step=10.0
        )
        
        new_bet_size = st.number_input(
            "Mise par Défaut (€)",
            min_value=0.1,
            value=float(config['default_bet_size']),
            step=1.0
        )
        
        if st.button("💾 Sauvegarder Configuration"):
            config['current_bankroll'] = new_bankroll
            config['default_bet_size'] = new_bet_size
            tracker.save_config(config)
            st.success("✅ Configuration sauvegardée!")
            st.rerun()
    
    with col2:
        st.subheader("🗂️ Gestion des Données")
        
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            if st.button("📥 Export Historique", help="Télécharger l'historique en CSV"):
                history_df = tracker.get_history()
                if not history_df.empty:
                    csv = history_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Télécharger CSV",
                        data=csv,
                        file_name=f"betting_history_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ Aucun historique à exporter")
        
        with col2_2:
            if st.button("🗑️ Reset Complet", help="⚠️ ATTENTION: Supprime tout l'historique!"):
                if st.checkbox("⚠️ Je confirme vouloir supprimer tout l'historique"):
                    # Reset des fichiers
                    if os.path.exists(tracker.history_file):
                        os.remove(tracker.history_file)
                    if os.path.exists(tracker.config_file):
                        os.remove(tracker.config_file)
                    
                    # Réinitialiser
                    tracker._initialize_files()
                    st.success("✅ Reset effectué!")
                    st.rerun()
    
    # Informations système
    st.markdown("---")
    st.subheader("ℹ️ Informations Système")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **📁 Fichiers de Données**
        - Historique: {'✅' if os.path.exists(tracker.history_file) else '❌'} `{tracker.history_file}`
        - Configuration: {'✅' if os.path.exists(tracker.config_file) else '❌'} `{tracker.config_file}`
        - Paris du jour: {'✅' if os.path.exists('data/bets_today.csv') else '❌'} `data/bets_today.csv`
        """)
    
    with col2:
        today_str = datetime.now().strftime("%Y-%m-%d")
        fixtures_today = glob.glob(f"data/raw/fixtures_*_{today_str}.json")
        odds_today = glob.glob(f"data/raw/odds_*_{today_str}.json")
        
        st.info(f"""
        **📊 Données du Jour**
        - Fichiers fixtures: {len(fixtures_today)}
        - Fichiers cotes: {len(odds_today)}
        - Rankings: {'✅' if os.path.exists('data/rankings.csv') else '❌'}
        - Prédictions LSTM: {'✅' if os.path.exists('data/lstm/predictions_today.csv') else '❌'}
        """)
    
    with col3:
        stats = tracker.get_statistics()
        st.info(f"""
        **📈 Statistiques Rapides**
        - Paris totaux: {stats['total_bets']}
        - Profit/Perte: {stats['profit_loss']:+.2f}€
        - ROI: {stats['roi_percentage']:+.1f}%
        - En attente: {stats['pending_bets']}
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏈 <strong>Football LSTM Betting Dashboard</strong> - Analyse intelligente des paris sportifs</p>
    <p>📊 Données en temps réel • 🤖 Prédictions LSTM • 💰 Gestion de bankroll • 📈 Historique complet</p>
</div>
""", unsafe_allow_html=True)