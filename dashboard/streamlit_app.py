# dashboard/streamlit_app.py
# -----------------------------------------------------------------------------
# Application Streamlit simple pour visualiser les performances du modèle,
# l’évolution du bankroll, et les statistiques des paris simulés (via Kelly).
# -----------------------------------------------------------------------------

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Titre de l'app
st.title("📊 Analyse des Paris Sportifs - Modèle LSTM + Kelly")

# Charger les données simulées
bankroll_history = np.loadtxt("data/lstm/kelly_backtest.csv", delimiter=",")

# Graphique bankroll
st.subheader("💰 Évolution du Bankroll")
fig, ax = plt.subplots()
ax.plot(bankroll_history)
ax.set_xlabel("Match #")
ax.set_ylabel("Bankroll (€)")
ax.grid(True)
st.pyplot(fig)

# Statistiques
st.subheader("📈 Statistiques")
roi = (bankroll_history[-1] - bankroll_history[0]) / bankroll_history[0] * 100
st.metric("ROI", f"{roi:.2f}%")

# Historique à afficher (optionnel)
# st.dataframe(...)
