# preprocessing/match_odds_mapper.py
# -----------------------------------------------------------------------------
# Ce script aligne les cotes Pinnacle avec les matchs issus d'API‑Football
# en utilisant l'ID du fixture.  Il s'appuie désormais sur le fichier CSV
# généré par ingestion/fetch_pinnacle_odds.py et sur le fichier
# data/processed/base_matches.csv produit par ingestion/merge_dataset.py.
# Le résultat est enregistré dans data/odds.csv pour être utilisé lors du
# backtest Kelly.
# -----------------------------------------------------------------------------

"""
Mapping entre les données de matchs et les cotes Pinnacle.

Ce module lit le fichier `data/processed/base_matches.csv`, censé contenir au
moins les colonnes `fixture_id`, `date`, `home` et `away`, ainsi que le
fichier `data/raw/pinnacle_odds.csv` généré par `ingestion/fetch_pinnacle_odds.py`.
Les deux jeux de données sont fusionnés via la clé `fixture_id` afin d'obtenir
les cotes pour chaque match.  La sortie est un CSV `data/odds.csv` prêt pour
l'évaluation.
"""

import os
import pandas as pd

# Chemins des fichiers d'entrée et de sortie
FIXTURES_PATH = "data/processed/base_matches.csv"
PINNACLE_ODDS_PATH = "data/raw/pinnacle_odds.csv"
OUTPUT_PATH = "data/odds.csv"


def main() -> None:
    # Vérifier l'existence des fichiers nécessaires
    if not os.path.exists(FIXTURES_PATH):
        print(f"❌ Fichier introuvable : {FIXTURES_PATH}")
        return
    if not os.path.exists(PINNACLE_ODDS_PATH):
        print(f"❌ Fichier introuvable : {PINNACLE_ODDS_PATH}")
        return
    try:
        fixtures_df = pd.read_csv(FIXTURES_PATH)
        odds_df = pd.read_csv(PINNACLE_ODDS_PATH)
        if fixtures_df.empty:
            print(f"⚠️ Fichier de fixtures vide : {FIXTURES_PATH}")
            return
        if odds_df.empty:
            print(f"⚠️ Fichier de cotes vide : {PINNACLE_ODDS_PATH}")
            return
        # Normaliser les noms de colonnes si nécessaire
        if "fixture_id" not in fixtures_df.columns:
            # Recherche d'un équivalent plausible
            cand_cols = [c for c in fixtures_df.columns if "fixture" in c.lower() and "id" in c.lower()]
            if cand_cols:
                fixtures_df = fixtures_df.rename(columns={cand_cols[0]: "fixture_id"})
            else:
                raise KeyError("Colonne `fixture_id` manquante dans base_matches.csv")
        # Fusionner sur fixture_id
        merged = fixtures_df.merge(odds_df, on="fixture_id", how="inner")
        if merged.empty:
            print("⚠️ Aucune correspondance trouvée entre fixtures et cotes.")
            return
        # Sélectionner des colonnes pertinentes
        cols_to_keep = []
        for col in ["fixture_id", "date", "home", "away", "odds_home", "odds_draw", "odds_away"]:
            if col in merged.columns:
                cols_to_keep.append(col)
        result = merged[cols_to_keep]
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        result.to_csv(OUTPUT_PATH, index=False)
        print(f"✅ Cotes mappées sauvegardées dans {OUTPUT_PATH} ({len(result)} lignes)")
    except Exception as e:
        print(f"❌ Erreur lors du mappage des cotes : {e}")


if __name__ == "__main__":
    main()
