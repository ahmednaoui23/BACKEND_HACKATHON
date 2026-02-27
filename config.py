import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Charge les variables contenues dans le fichier .env
load_dotenv()

db = SQLAlchemy()

class Config:
    # Récupère l'URL depuis le .env, sinon utilise une valeur vide par défaut
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False