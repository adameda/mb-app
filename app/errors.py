"""Gestionnaires d'erreurs personnalisés"""
from flask import render_template
from app import db


def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs pour l'application
    
    Args:
        app: L'instance Flask
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Gère les erreurs 404 (page non trouvée)
        
        Args:
            error: L'erreur levée
            
        Returns:
            Template 404 avec code HTTP 404
        """
        # Log l'accès à une page inexistante
        app.logger.warning(f'Page non trouvée: {error}')
        return render_template('errors/404.html'), 404
    
    
    @app.errorhandler(500)
    def internal_error(error):
        """Gère les erreurs 500 (erreur serveur interne)
        
        Args:
            error: L'erreur levée
            
        Returns:
            Template 500 avec code HTTP 500
        """
        # Rollback de la session DB en cas d'erreur
        db.session.rollback()
        
        # Log l'erreur avec tous les détails (IMPORTANT pour debug)
        app.logger.error(f'Erreur serveur 500: {error}', exc_info=True)
        
        return render_template('errors/500.html'), 500
    
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Gère les erreurs 403 (accès interdit)
        
        Args:
            error: L'erreur levée
            
        Returns:
            Template 403 avec code HTTP 403
        """
        # Log les tentatives d'accès non autorisé
        app.logger.warning(f'Accès interdit: {error}')
        return render_template('errors/403.html'), 403
