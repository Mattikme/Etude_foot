# pipeline/test_ingestion.py
import os
import subprocess

print("🔍 Test de l'ingestion des données...\n")

steps = [
    "python ingestion/fetch_fixtures.py",
    "python ingestion/fetch_stats.py",
    "python ingestion/fetch_odds_api_football.py"
]

for cmd in steps:
    print(f"🚀 Exécution de : {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Erreur : {cmd} a échoué.\n")
    else:
        print(f"✅ Succès : {cmd} terminé.\n")

print("📂 Contenu du dossier data/raw :")
if not os.path.exists("data/raw"):
    print("❌ Le dossier data/raw n'existe pas.")
else:
    files = os.listdir("data/raw")
    if not files:
        print("⚠️ Aucun fichier trouvé dans data/raw.")
    else:
        for f in sorted(files):
            print(f"   📄 {f}")
