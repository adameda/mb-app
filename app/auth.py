"""Module d'authentification"""
import os
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    """Classe utilisateur simple pour l'authentification
    
    Pour l'instant, un seul utilisateur admin défini dans .env
    Plus tard, on pourra migrer vers une table en base de données
    """
    
    def __init__(self, username):
        self.id = username
        self.username = username
    
    @staticmethod
    def get(username):
        """Récupère un utilisateur par son username
        
        Args:
            username: Le nom d'utilisateur
            
        Returns:
            User si les identifiants correspondent, None sinon
        """
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        
        if username == admin_username:
            return User(username)
        return None
    
    @staticmethod
    def authenticate(username, password):
        """Vérifie les identifiants de connexion
        
        Args:
            username: Le nom d'utilisateur
            password: Le mot de passe
            
        Returns:
            User si authentification réussie, None sinon
        """
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password_hash = os.environ.get('ADMIN_PASSWORD_HASH')
        
        if not admin_username or not admin_password_hash:
            return None
        
        if username == admin_username and check_password_hash(admin_password_hash, password):
            return User(username)
        return None


def load_user(user_id):
    """Fonction pour charger l'utilisateur (requis par Flask-Login)
    
    Args:
        user_id: L'identifiant de l'utilisateur
        
    Returns:
        User ou None
    """
    return User.get(user_id)
