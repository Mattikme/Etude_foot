# Prédictor de résultats football API-Football

## 🚀 Objectif du projet

Ce projet open-source permet de prédire les résultats de matchs de football à partir de données fournies par l'API-Football. Il combine des scripts d'extraction, d'analyse, de traitement des données et de visualisation des probabilités de victoire basées sur plusieurs stratégies.

Le but final est de proposer des **pronostics intelligents** pouvant être comparés aux cotes réelles des bookmakers (Bet365, Pinnacle, etc.) et repérer des **valeurs (value bets)**.

---

## 📝 Fonctionnalités principales

* 📊 Collecte automatique des matchs du jour pour de nombreuses ligues
* 🔬 Récupération des statistiques, compositions, et cotes
* 🧬 Application de stratégies de prédiction (ELO, forme récente, stats, etc.)
* 📈 Enregistrement des données brutes et transformées (JSON)
* 🔗 Comparaison avec les cotes pour repérer des valeurs
* 🌐 Visualisation future des paris suggérés (en cours de développement)

---

## 🤧 Structure technique

```
api-football-predictor/
├── config/                  # Configuration API, ligues cibles, chemins
├── data/
│   ├── raw/               # Fichiers bruts : fixtures, odds, stats, lineups
│   └── processed/         # Prédictions, matchups avec analyse
├── ingestion/               # Scripts de collecte de données (fetch_*.py)
├── pipeline/                # Script principal : run_pipeline.py
├── utils/                   # Fonctions communes : requêtes, stratégies
├── notebooks/               # Analyses exploratoires (optionnel)
├── outputs/                 # Logs, prédictions futures (format lisible)
└── README.md                # Document actuel
```

---

## 🔢 Fonctionnement

### 1. Configuration

* Clé API à ajouter dans `config/api_keys.yaml` :

```yaml
api_football:
  key: VOTRE_CLE
  host: v3.football.api-sports.io
```

* Ligues cibles dans `config/target_league_ids.yaml` (dict ou liste d'IDs)

---

### 2. Pipeline principal

Lancement manuel ou via GitHub Actions :

```bash
python pipeline/run_pipeline.py
```

Ce script :

1. Récupère les matchs du jour (`fixtures`)
2. Récupère stats, cotes et compositions par match
3. Applique les stratégies de prédiction
4. Sauvegarde les outputs dans `data/processed/`

---

### 3. Stratégies de prédiction

* ELO (classement dynamique)
* Comparaison stats domicile / extérieur
* Forme récente (victoires, buts)
* Alignements d'équipe (optionnel)
* Possibilité d'ajouter vos propres méthodes dans `utils/strategies.py`

---

### 4. Cotes bookmakers

* Requêtes par match sur `/odds?fixture=<id>&bookmaker=8` (Bet365)
* Stockage dans `data/raw/odds_<fixture_id>.json`

---

### 5. Analyse des values

Une fois les probabilités estimées, le système calcule si la cote propose une **value** :

```python
value = (proba_estimee * cote_bookmaker) - 1 > 0.05
```

---

## 📊 Visualisation (future)

* Une interface Streamlit ou web est prévue pour afficher les matchs du jour avec :

  * Probabilités prédites vs. cotes Bet365
  * Mise recommandée
  * Historique des performances

---

## 🚧 En cours ou idées d'amélioration

* Modèle ML / xG basé sur historique complet
* Intégration avec Telegram ou email (alerte value bets)
* Historique ELO global
* Simulateur de bankroll

---

## 📆 Automatisation

* GitHub Actions exécute le pipeline chaque jour
* Workflow `run-pipeline.yml` déclenche :

  * `run_pipeline.py`
  * et consigne tous les logs dans les artefacts

---

## 🚫 Limitations / Conseils

* Le modèle **ne garantit pas** un profit : c'est un outil de soutien
* Ne pas parier au-delà de vos moyens
* API RapidAPI a des quotas : préférez la clé directe API-Football si possible

---

## 🎓 Sources utiles

* [API-Football Docs](https://www.api-football.com/documentation)
* [RapidAPI Endpoint Explorer](https://rapidapi.com/api-sports/api/api-football)
* Modèles inspirés des travaux d'évaluation ELO + value betting

---

## 🚀 Lancement rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Ajouter vos clés et ligues dans /config

# 3. Lancer le pipeline
python pipeline/run_pipeline.py

# 4. Consulter les fichiers data/processed/
```

---

**Bon prono ⚽ ✨ et pariez de manière responsable.**
 
