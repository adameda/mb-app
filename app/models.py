"""Modèles de base de données"""
from datetime import datetime, date
from app import db

class Client(db.Model):
    """Modèle pour les clients"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    entreprise = db.Column(db.String(200))
    adresse = db.Column(db.Text)
    ville = db.Column(db.String(100))
    code_postal = db.Column(db.String(10))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    devis = db.relationship('Devis', backref='client', lazy=True, cascade='all, delete-orphan')
    factures = db.relationship('Facture', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.nom}>'


class PrixCatalogue(db.Model):
    """Catalogue des prix"""
    __tablename__ = 'prix_catalogue'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # Ex: T1, D1, etc.
    categorie = db.Column(db.String(50), nullable=False)  # TOLERIE_CARROSSERIE, DEBOSSELAGE
    description = db.Column(db.String(200))
    prix = db.Column(db.Float, nullable=False)
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PrixCatalogue {self.code} - {self.prix}€>'


class Devis(db.Model):
    """Modèle pour les devis"""
    __tablename__ = 'devis'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)  # Ex: N°003
    date = db.Column(db.Date, nullable=False, default=date.today)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Informations additionnelles
    numero_serie = db.Column(db.String(100))  # Immatriculation
    inventaire = db.Column(db.String(100))
    statut = db.Column(db.String(20), default='brouillon')  # brouillon, envoye, accepte, refuse
    validite_jours = db.Column(db.Integer, default=30)  # 1 mois par défaut
    
    # Totaux
    total_ht = db.Column(db.Float, default=0.0)
    total_ttc = db.Column(db.Float, default=0.0)
    
    # Remise et acompte
    remise_pourcent = db.Column(db.Float, default=0.0)
    acompte = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    lignes = db.relationship('DevisLigne', backref='devis', lazy=True, cascade='all, delete-orphan')
    facture = db.relationship('Facture', backref='devis', uselist=False, cascade='all, delete-orphan')
    
    def calculer_totaux(self):
        """Calcule et met à jour les totaux HT et TTC du devis"""
        total_ht_brut = 0.0
        total_ttc = 0.0
        
        # Calculer le total HT brut
        for ligne in self.lignes:
            montant_ht = ligne.prix_unitaire_ht * ligne.quantite
            total_ht_brut += montant_ht
        
        # Appliquer la remise sur le HT
        remise_montant = total_ht_brut * (self.remise_pourcent / 100)
        total_ht_apres_remise = total_ht_brut - remise_montant
        
        # Calculer le TTC avec la remise appliquée
        for ligne in self.lignes:
            montant_ht = ligne.prix_unitaire_ht * ligne.quantite
            montant_ht_apres_remise = montant_ht * (1 - self.remise_pourcent / 100)
            montant_tva = montant_ht_apres_remise * (ligne.tva_pourcent / 100)
            total_ttc += montant_ht_apres_remise + montant_tva
        
        # Mettre à jour les totaux
        self.total_ht = total_ht_apres_remise
        self.total_ttc = total_ttc
    
    def __repr__(self):
        return f'<Devis {self.numero}>'


class DevisLigne(db.Model):
    """Lignes d'un devis"""
    __tablename__ = 'devis_lignes'
    
    id = db.Column(db.Integer, primary_key=True)
    devis_id = db.Column(db.Integer, db.ForeignKey('devis.id'), nullable=False)
    
    # Informations de la ligne
    tache = db.Column(db.String(100))  # Ex: TOLERIE_CARROSSERIE
    vehicule = db.Column(db.String(20))  # Ex: 0
    description = db.Column(db.String(200))  # Ex: test
    quantite = db.Column(db.Integer, default=1)
    unite = db.Column(db.String(20))  # Ex: T3, DS
    prix_unitaire_ht = db.Column(db.Float, nullable=False)
    tva_pourcent = db.Column(db.Float, default=0.0)
    total_ttc = db.Column(db.Float, nullable=False)
    
    ordre = db.Column(db.Integer)  # Pour garder l'ordre des lignes
    
    def __repr__(self):
        return f'<DevisLigne {self.description}>'


class Facture(db.Model):
    """Modèle pour les factures"""
    __tablename__ = 'factures'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)  # Ex: 001
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    # Liaisons
    devis_id = db.Column(db.Integer, db.ForeignKey('devis.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Montants
    montant_ttc = db.Column(db.Float, nullable=False)
    acompte = db.Column(db.Float, default=0.0)
    reste_a_payer = db.Column(db.Float, nullable=False)
    
    # Paiement
    etat_paiement = db.Column(db.String(50), default='En attente')  # En attente, Paiement partiel, Payé
    mode_paiement = db.Column(db.String(50))  # Paiement par virement, Espèces, Chèque, Carte bancaire
    date_paiement = db.Column(db.Date)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Facture {self.numero}>'


class Config(db.Model):
    """Configuration de l'entreprise"""
    __tablename__ = 'config'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations entreprise
    nom_entreprise = db.Column(db.String(200), nullable=False)
    adresse = db.Column(db.Text)
    ville = db.Column(db.String(100))
    code_postal = db.Column(db.String(10))
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Informations légales
    siret = db.Column(db.String(50))
    tva_intra = db.Column(db.String(50))
    
    # Coordonnées bancaires
    iban = db.Column(db.String(100))
    bic = db.Column(db.String(20))
    banque = db.Column(db.String(100))
    
    # Mentions légales
    mentions_legales = db.Column(db.Text)
    
    # Logo
    logo_path = db.Column(db.String(255))
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Config {self.nom_entreprise}>'
