# API Football Predictor

## 📄 Objectif

Ce projet prédit les résultats de matchs de football à l’aide de données issues de l’API-Football sur RAPIDAPI. Il couvre toutes les étapes : ingestion, prétraitement, modélisation (LSTM), détection de value bets, et évaluation automatique des résultats.

---

## 📁 Structure du répertoire

```
api-football-predictor/
├── data/                         # Données collectées et générées
│   ├── raw/                     # JSONs bruts (fixtures, odds, standings, etc.)
│   │   ├── fixtures_*.json     # Matchs par ligue et date
│   │   ├── odds_*.json         # Cotes associées aux matchs
│   │   └── standings/          # Classements par ligue (JSON)
│   ├── processed/              # Fichiers CSV prêts pour modélisation
│   │   └── base_matches.csv    # Fichier fusionné principal (features + cotes)
│   ├── lstm/                   # Séquences LSTM + prédictions
│   ├── bets_today.csv          # Value bets détectés aujourd’hui
│   ├── bets_YYYY-MM-DD.csv     # Bets d’un jour précis
│   ├── bets_results_*.csv      # Résultats évalués (gagné ou perdu)
│   └── rankings.csv            # Classement pondéré généré (importance des équipes)
│
├── ingestion/                  # Scripts de récupération via l'API
│   ├── fetch_fixtures.py       # Matchs à venir
│   ├── fetch_stats.py          # Statistiques complètes de match
│   ├── fetch_lineups.py        # Compositions d’équipes
│   ├── fetch_events.py         # Evénements (buts, cartons, etc.)
│   ├── fetch_injuries.py       # Blessures
│   ├── fetch_standings.py      # Classements de ligue (pour ranking)
│   ├── fetch_player_stats.py   # Statistiques individuelles des joueurs
│   └── fetch_odds_api_football.py  # Cotes des bookmakers

├── preprocessing/              # Préparation des données
│   ├── match_odds_mapper.py    # Fusionne les odds avec les features
│   ├── create_lstm_sequences.py# Préparation des données LSTM
│   └── generate_rankings.py       # Classement pondéré des équipes

├── modeling/                   # Modèle de prédiction
│   └── lstm_model.py             # Réseau de neurones LSTM pour issue match

├── evaluation/                 # Outils d'évaluation
│   ├── backtest_kelly.py         # Backtest via critère de Kelly
│   └── evaluate_bets.py          # Analyse réelle des bets d’hier

├── pipeline/                   # Orchestration complète
│   └── run_pipeline.py          # Lance toutes les étapes automatiquement

├── utils/                      # Outils génériques
│   └── request_handler.py       # Appel API avec gestion d’erreur/temporisation

├── .env                        # Contient API_FOOTBALL_KEY
├── requirements.txt            # Dépendances Python
└── README.md                   # Ce fichier
```

---

## ⚡ Lancer le pipeline automatiquement

```bash
python pipeline/run_pipeline.py
```

Cela :

* collecte les données
* génère `base_matches.csv` et `rankings.csv`
* lance le modèle LSTM
* identifie les value bets dans `data/bets_today.csv`
* évalue les paris d’hier automatiquement si disponibles

---

## 🔍 Analyse des fichiers clefs

### Données `data/`

* `data/raw/fixtures_*.json` : données de chaque match par ligue
* `data/processed/base_matches.csv` : ensemble fusionné avec toutes les features utiles
* `data/bets_today.csv` : tableau des meilleurs value bets du jour (triés)
* `data/rankings.csv` : score des équipes calculé à partir des standings

### Ingestion `ingestion/`

* Chaque script appelle l'API-Football pour un type précis de donnée

### Traitement `preprocessing/`

* `generate_rankings.py` : transforme les standings API en score unique d’équipe
* `match_odds_mapper.py` : fusionne cotes + classement + features en table finale

### Modélisation `modeling/`

* `lstm_model.py` : prédit les probabilités de Home / Draw / Away

### Evaluation `evaluation/`

* `backtest_kelly.py` : simule les bets avec mise proportionnelle
* `evaluate_bets.py` : vérifie si les paris d’hier étaient gagnants ou non

### Pipeline `run_pipeline.py`

* Orchestre toutes les étapes, y compris :

  * génération automatique des rankings
  * analyse automatique des paris
  * sauvegarde des résultats de la veille

---

## 📆 Exemple de sortie `data/bets_today.csv`

| match        | bet\_on | bookmaker\_odds | expected\_prob | expected\_value |
| ------------ | ------- | --------------- | -------------- | --------------- |
| Lyon vs Nice | Home    | 2.35            | 0.55           | 0.29            |

---

## 🤝 Améliorations possibles

* Calibration dynamique des expected\_prob
* Modèle XGBoost ou Deep Learning supplémentaire
* Dashboard interactif avec Streamlit

---

## 👤 Auteur

* [@Matttgic](https://github.com/Matttgic)

---

## 📚 Licence

MIT
