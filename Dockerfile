# Dockerfile
# -----------------------------------------------------------------------------
# Dockerisation du projet de prédiction LSTM football avec API-Football + Pinnacle
# Conteneur exécutable avec tout l’environnement (librairies, scripts, Streamlit)
# -----------------------------------------------------------------------------

FROM python:3.11-slim

# Définir le dossier de travail dans le conteneur
WORKDIR /app

# Copier les fichiers du projet
COPY . /app

# Installer les dépendances
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Port pour Streamlit (si besoin)
EXPOSE 8501

# Commande par défaut (modifiable)
CMD ["python", "pipeline/run_pipeline.py"]
