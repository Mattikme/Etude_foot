# README.md
# -----------------------------------------------------------------------------
# Documentation du projet : Prédiction de résultats football avec LSTM + Kelly
# Collecte via API-Football & Pinnacle Odds | Deep Learning & Backtest intégré
# -----------------------------------------------------------------------------

## ⚽ Objectif
Créer un pipeline complet pour prédire les résultats de matchs de football, en se basant sur les données API-Football et les cotes Pinnacle Odds, avec un modèle LSTM et une stratégie de bankroll via le critère de Kelly.

---

## 🧱 Structure du projet

```
project-root/
│
├── config/                  # Clés API (non versionnées)
│   ├── api_keys.yaml
│   └── pinnacle_keys.yaml
│
├── data/                   # Données brutes et traitées
│   ├── raw/
│   ├── processed/
│   ├── lstm/
│   └── odds.csv
│
├── ingestion/              # Scripts de récupération API
├── preprocessing/          # Nettoyage, mapping, séquences LSTM
├── modeling/               # Modèle LSTM Keras
├── evaluation/             # Backtest Kelly
├── dashboard/              # Visualisation Streamlit
├── pipeline/               # Orchestration pipeline
│
└── README.md
```

---

## 🔧 Lancer le pipeline complet
```bash
python pipeline/run_pipeline.py
```

## 🧠 Modèle utilisé
- LSTM simple (64 neurones)
- Features : résultats précédents sur 5 matchs glissants
- Cible : victoire domicile, nul, ou défaite

## 🧪 Stratégie bankroll
- Critère de Kelly (fractionnaire)
- Application sur les cotes réelles Pinnacle
- ROI et évolution simulée du capital

## 📊 Dashboard
```bash
streamlit run dashboard/streamlit_app.py
```

---

## 🔐 Sécurité & Bonnes pratiques
- Clés API stockées en YAML dans `config/`, ignorées via `.gitignore`
- Requêtes centralisées dans `request_handler.py`

---

## ✅ À venir
- Support live betting & in-play
- Fine-tuning des modèles
- Ajout des markets secondaires (BTTS, Over/Under, etc.)
