"""Point d'entrée de l'application"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from app.config import Config

# Extensions Flask
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialiser les extensions
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    # Configuration de Flask-Login
    login_manager.login_view = 'login'  # Redirige vers /login si non connecté
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # User loader pour Flask-Login
    from app.auth import User, load_user
    login_manager.user_loader(load_user)
    
    # Context processor pour rendre datetime disponible dans les templates
    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}
    
    # Configuration du logging (enregistrement des erreurs)
    if not app.debug:  # Seulement en production
        import os
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Créer le dossier logs s'il n'existe pas
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configurer le fichier de log avec rotation
        file_handler = RotatingFileHandler(
            'logs/mb-app.log',
            maxBytes=10240000,  # 10 MB (augmenté pour plus d'historique)
            backupCount=10      # Garde 10 fichiers de backup
        )
        
        # Format des logs : date - niveau - message
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('🚀 MB App démarré')
    
    # Enregistrer les gestionnaires d'erreurs
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # Importer et enregistrer les routes
    with app.app_context():
        from app import routes
        
        # Créer les tables de la base de données
        db.create_all()
    
    return app
