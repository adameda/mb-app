"""Formulaires WTForms pour l'application"""
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from datetime import date


class ClientForm(FlaskForm):
    """Formulaire pour créer/éditer un client"""
    nom = StringField('Nom', validators=[DataRequired(message='Le nom est requis')])
    entreprise = StringField('Entreprise', validators=[Optional()])
    adresse = TextAreaField('Adresse', validators=[Optional()])
    ville = StringField('Ville', validators=[Optional()])
    code_postal = StringField('Code postal', validators=[Optional()])
    telephone = StringField('Téléphone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email(message='Email invalide')])


class PrixForm(FlaskForm):
    """Formulaire pour créer/éditer un prix catalogue"""
    code = StringField('Code', validators=[DataRequired(message='Le code est requis')])
    categorie = SelectField('Catégorie', 
                          choices=[
                              ('TOLERIE_CARROSSERIE', 'Tôlerie / Carrosserie'),
                              ('DEBOSSELAGE', 'Débosselage')
                          ],
                          validators=[DataRequired(message='La catégorie est requise')])
    description = StringField('Description', validators=[Optional()])
    prix = FloatField('Prix (€)', validators=[
        DataRequired(message='Le prix est requis'),
        NumberRange(min=0, message='Le prix doit être positif')
    ])
    actif = BooleanField('Actif', default=True)


class DevisForm(FlaskForm):
    """Formulaire pour créer/éditer un devis"""
    client_id = SelectField('Client', coerce=int, validators=[DataRequired(message='Le client est requis')])
    date = DateField('Date', default=date.today, validators=[DataRequired(message='La date est requise')])
    numero_serie = StringField('N° série / Immatriculation', validators=[Optional()])
    inventaire = StringField('Inventaire', validators=[Optional()])
    validite_jours = IntegerField('Validité (jours)', default=30, validators=[
        DataRequired(message='La validité est requise'),
        NumberRange(min=1, message='La validité doit être au moins 1 jour')
    ])
    remise_pourcent = FloatField('Remise (%)', default=0.0, validators=[
        Optional(),
        NumberRange(min=0, max=100, message='La remise doit être entre 0 et 100%')
    ])
    acompte = FloatField('Acompte (€)', default=0.0, validators=[
        Optional(),
        NumberRange(min=0, message='L\'acompte doit être positif')
    ])
    statut = SelectField('Statut', 
                        choices=[
                            ('brouillon', 'Brouillon'),
                            ('envoye', 'Envoyé'),
                            ('accepte', 'Accepté'),
                            ('refuse', 'Refusé')
                        ],
                        default='brouillon',
                        validators=[DataRequired(message='Le statut est requis')])
