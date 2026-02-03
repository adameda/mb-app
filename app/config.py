"""Configuration de l'application Flask"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """Configuration de base"""
    
    # Clé secrète pour les sessions et CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Identifiants admin (pour l'authentification simple)
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')

    # Validation des variables obligatoires
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY doit être définie dans .env")
    if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
        raise ValueError("ADMIN_USERNAME et ADMIN_PASSWORD_HASH doivent être définis dans .env")
    
    # Base de données (PostgreSQL en prod, SQLite en dev)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///devis.db'
    
    # Fix pour Railway/Heroku qui utilisent 'postgres://' au lieu de 'postgresql://'
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sécurité des cookies de session
    SESSION_COOKIE_HTTPONLY = True  # Empêche JavaScript d'accéder au cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protection CSRF supplémentaire
    PERMANENT_SESSION_LIFETIME = 3600  # Session expire après 1 heure
    
    # En production (Railway détecte automatiquement HTTPS)
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        SESSION_COOKIE_SECURE = True  # Cookie uniquement via HTTPS
    
    # Configuration email (optionnel pour l'instant)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Limite de taille des requêtes (protection contre saturation)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max