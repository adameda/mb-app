"""Routes de l'application"""
import json
from flask import render_template, redirect, url_for, flash, request, jsonify, make_response, current_app as app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Client, Devis, Facture, PrixCatalogue, DevisLigne, Config
from app.forms import ClientForm, PrixForm, DevisForm
from app.auth import User
from datetime import datetime, date


# ========== ROUTES AUTHENTIFICATION ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    # Si déjà connecté, rediriger vers l'accueil
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vérifier les identifiants
        user = User.authenticate(username, password)
        
        if user:
            login_user(user, remember=True)
            # Log succès avec IP pour traçabilité
            app.logger.info(f'✅ Connexion réussie - User: {username} - IP: {request.remote_addr}')
            flash('Connexion réussie !', 'success')
            
            # Rediriger vers la page demandée ou l'accueil
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            # Log échec pour détecter les attaques
            app.logger.warning(f'⚠️ Tentative de connexion échouée - User: {username} - IP: {request.remote_addr}')
            flash('Identifiants incorrects. Veuillez réessayer.', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    username = current_user.username
    # Log déconnexion avec IP
    app.logger.info(f'👋 Déconnexion - User: {username} - IP: {request.remote_addr}')
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))


# ========== DASHBOARD ==========

@app.route('/')
@login_required
def index():
    """Page d'accueil - Dashboard"""
    # Statistiques rapides
    nb_clients = Client.query.count()
    nb_devis = Devis.query.count()
    nb_factures = Facture.query.count()
    
    # Derniers devis
    derniers_devis = Devis.query.order_by(Devis.created_at.desc()).limit(5).all()
    
    return render_template('index.html',
                         nb_clients=nb_clients,
                         nb_devis=nb_devis,
                         nb_factures=nb_factures,
                         derniers_devis=derniers_devis)


# ========== ROUTES CLIENTS ==========

@app.route('/clients')
@login_required
def clients_liste():
    """Liste tous les clients"""
    search = request.args.get('search', '')
    
    if search:
        clients = Client.query.filter(
            db.or_(
                Client.nom.ilike(f'%{search}%'),
                Client.entreprise.ilike(f'%{search}%'),
                Client.email.ilike(f'%{search}%')
            )
        ).order_by(Client.nom).all()
    else:
        clients = Client.query.order_by(Client.nom).all()
    
    return render_template('clients/liste.html', clients=clients, search=search)


@app.route('/clients/ajouter', methods=['GET', 'POST'])
@login_required
def client_ajouter():
    """Ajouter un nouveau client"""
    form = ClientForm()
    
    if form.validate_on_submit():
        client = Client(
            nom=form.nom.data,
            entreprise=form.entreprise.data,
            adresse=form.adresse.data,
            ville=form.ville.data,
            code_postal=form.code_postal.data,
            telephone=form.telephone.data,
            email=form.email.data
        )
        db.session.add(client)
        db.session.commit()
        
        flash(f'Client {client.nom} ajouté avec succès !', 'success')
        return redirect(url_for('clients_liste'))
    
    return render_template('clients/form.html', form=form, title='Ajouter un client')


@app.route('/clients/<int:id>/editer', methods=['GET', 'POST'])
@login_required
def client_editer(id):
    """Éditer un client existant"""
    client = Client.query.get_or_404(id)
    form = ClientForm(obj=client)
    
    if form.validate_on_submit():
        form.populate_obj(client)
        db.session.commit()
        
        flash(f'Client {client.nom} modifié avec succès !', 'success')
        return redirect(url_for('clients_liste'))
    
    return render_template('clients/form.html', form=form, title='Éditer le client', client=client)


@app.route('/clients/<int:id>/supprimer', methods=['POST'])
@login_required
def client_supprimer(id):
    """Supprimer un client"""
    client = Client.query.get_or_404(id)
    nom = client.nom
    
    db.session.delete(client)
    db.session.commit()
    
    app.logger.info(f'Client supprimé: {nom} (ID: {id})')
    flash(f'Client {nom} supprimé avec succès !', 'success')
    return redirect(url_for('clients_liste'))


# ========== ROUTES PRIX ==========

@app.route('/prix')
@login_required
def prix_liste():
    """Liste tous les prix du catalogue"""
    categorie_filter = request.args.get('categorie', '')
    
    if categorie_filter:
        prix = PrixCatalogue.query.filter_by(categorie=categorie_filter).order_by(PrixCatalogue.code).all()
    else:
        prix = PrixCatalogue.query.order_by(PrixCatalogue.categorie, PrixCatalogue.code).all()
    
    return render_template('prix/liste.html', prix=prix, categorie_filter=categorie_filter)


@app.route('/prix/ajouter', methods=['GET', 'POST'])
@login_required
def prix_ajouter():
    """Ajouter un nouveau prix"""
    form = PrixForm()
    
    if form.validate_on_submit():
        # Vérifier que le code n'existe pas déjà
        existing = PrixCatalogue.query.filter_by(code=form.code.data).first()
        if existing:
            flash(f'Un prix avec le code {form.code.data} existe déjà !', 'error')
        else:
            prix = PrixCatalogue(
                code=form.code.data,
                categorie=form.categorie.data,
                description=form.description.data,
                prix=form.prix.data,
                actif=form.actif.data
            )
            db.session.add(prix)
            db.session.commit()
            
            flash(f'Prix {prix.code} ajouté avec succès !', 'success')
            return redirect(url_for('prix_liste'))
    
    return render_template('prix/form.html', form=form, title='Ajouter un prix')


@app.route('/prix/<int:id>/editer', methods=['GET', 'POST'])
@login_required
def prix_editer(id):
    """Éditer un prix existant"""
    prix = PrixCatalogue.query.get_or_404(id)
    form = PrixForm(obj=prix)
    
    if form.validate_on_submit():
        # Vérifier si le code a changé et s'il existe déjà
        if form.code.data != prix.code:
            existing = PrixCatalogue.query.filter_by(code=form.code.data).first()
            if existing:
                flash(f'Un prix avec le code {form.code.data} existe déjà !', 'error')
                return render_template('prix/form.html', form=form, title='Éditer le prix', prix=prix)
        
        form.populate_obj(prix)
        db.session.commit()
        
        flash(f'Prix {prix.code} modifié avec succès !', 'success')
        return redirect(url_for('prix_liste'))
    
    return render_template('prix/form.html', form=form, title='Éditer le prix', prix=prix)


@app.route('/prix/<int:id>/supprimer', methods=['POST'])
@login_required
def prix_supprimer(id):
    """Supprimer un prix"""
    prix = PrixCatalogue.query.get_or_404(id)
    code = prix.code
    
    db.session.delete(prix)
    db.session.commit()
    
    flash(f'Prix {code} supprimé avec succès !', 'success')
    return redirect(url_for('prix_liste'))


# ========== ROUTES DEVIS ==========

@app.route('/devis')
@login_required
def devis_liste():
    """Liste tous les devis"""
    search = request.args.get('search', '')
    statut_filter = request.args.get('statut', '')
    
    query = Devis.query
    
    if search:
        query = query.join(Client).filter(
            db.or_(
                Devis.numero.ilike(f'%{search}%'),
                Client.nom.ilike(f'%{search}%')
            )
        )
    
    if statut_filter:
        query = query.filter_by(statut=statut_filter)
    
    devis = query.order_by(Devis.created_at.desc()).all()
    
    return render_template('devis/liste.html', devis=devis, search=search, statut_filter=statut_filter)


@app.route('/devis/nouveau', methods=['GET', 'POST'])
@login_required
def devis_nouveau():
    """Créer un nouveau devis"""
    form = DevisForm()
    
    # Charger les clients pour le select
    form.client_id.choices = [(c.id, f"{c.nom} {('- ' + c.entreprise) if c.entreprise else ''}") for c in Client.query.order_by(Client.nom).all()]
    
    if form.validate_on_submit():
        # Générer le numéro de devis
        dernier_devis = Devis.query.order_by(Devis.id.desc()).first()
        if dernier_devis and dernier_devis.numero:
            # Extraire le numéro et incrémenter
            try:
                dernier_num = int(dernier_devis.numero.replace('N°', ''))
                nouveau_num = f"N°{str(dernier_num + 1).zfill(3)}"
            except (ValueError, AttributeError):
                nouveau_num = "N°001"
        else:
            nouveau_num = "N°001"
        
        # Créer le devis
        devis = Devis(
            numero=nouveau_num,
            date=form.date.data,
            client_id=form.client_id.data,
            numero_serie=form.numero_serie.data,
            inventaire=form.inventaire.data,
            validite_jours=form.validite_jours.data,
            remise_pourcent=form.remise_pourcent.data,
            acompte=form.acompte.data,
            statut=form.statut.data
        )
        
        # Récupérer les lignes du formulaire (envoyées via JSON)
        lignes_data = request.form.get('lignes_json')
        if lignes_data:
            lignes = json.loads(lignes_data)
            
            for idx, ligne_data in enumerate(lignes):
                ligne = DevisLigne(
                    tache=ligne_data.get('tache', ''),
                    vehicule=ligne_data.get('vehicule', ''),
                    description=ligne_data.get('description', ''),
                    quantite=int(ligne_data.get('quantite', 1)),
                    unite=ligne_data.get('unite', ''),
                    prix_unitaire_ht=float(ligne_data.get('prix_unitaire_ht', 0)),
                    tva_pourcent=float(ligne_data.get('tva_pourcent', 0)),
                    total_ttc=float(ligne_data.get('total_ttc', 0)),
                    ordre=idx + 1
                )
                devis.lignes.append(ligne)
            
            # Calculer les totaux via la méthode du modèle
            devis.calculer_totaux()
        
        db.session.add(devis)
        db.session.commit()
        
        flash(f'Devis {devis.numero} créé avec succès !', 'success')
        return redirect(url_for('devis_liste'))
    
    # Charger les prix pour le formulaire
    prix_catalogue = PrixCatalogue.query.filter_by(actif=True).order_by(PrixCatalogue.categorie, PrixCatalogue.code).all()
    
    return render_template('devis/form.html', 
                         form=form, 
                         title='Nouveau devis',
                         lignes_dict=[],
                         prix_catalogue=prix_catalogue)


@app.route('/devis/<int:id>')
def devis_voir(id):
    """Voir les détails d'un devis"""
    devis = Devis.query.get_or_404(id)
    return render_template('devis/voir.html', devis=devis)


@app.route('/devis/<int:id>/editer', methods=['GET', 'POST'])
@login_required
def devis_editer(id):
    """Éditer un devis existant"""
    devis = Devis.query.get_or_404(id)
    
    # Vérifier si le devis est verrouillé
    if devis.statut == 'accepte' or devis.facture:
        flash('⚠️ Ce devis est verrouillé car il a été accepté ou converti en facture. Vous ne pouvez plus le modifier.', 'error')
        return redirect(url_for('devis_voir', id=id))
    
    form = DevisForm(obj=devis)
    
    # Charger les clients pour le select
    form.client_id.choices = [(c.id, f"{c.nom} {('- ' + c.entreprise) if c.entreprise else ''}") for c in Client.query.order_by(Client.nom).all()]
    
    if form.validate_on_submit():
        devis.date = form.date.data
        devis.client_id = form.client_id.data
        devis.numero_serie = form.numero_serie.data
        devis.inventaire = form.inventaire.data
        devis.validite_jours = form.validite_jours.data
        devis.remise_pourcent = form.remise_pourcent.data
        devis.acompte = form.acompte.data
        devis.statut = form.statut.data
        
        # Mettre à jour les lignes
        lignes_data = request.form.get('lignes_json')
        if lignes_data:
            lignes = json.loads(lignes_data)
            
            # Supprimer les anciennes lignes
            DevisLigne.query.filter_by(devis_id=devis.id).delete()
            
            for idx, ligne_data in enumerate(lignes):
                ligne = DevisLigne(
                    devis_id=devis.id,
                    tache=ligne_data.get('tache', ''),
                    vehicule=ligne_data.get('vehicule', ''),
                    description=ligne_data.get('description', ''),
                    quantite=int(ligne_data.get('quantite', 1)),
                    unite=ligne_data.get('unite', ''),
                    prix_unitaire_ht=float(ligne_data.get('prix_unitaire_ht', 0)),
                    tva_pourcent=float(ligne_data.get('tva_pourcent', 0)),
                    total_ttc=float(ligne_data.get('total_ttc', 0)),
                    ordre=idx + 1
                )
                db.session.add(ligne)
            
            # Refresh pour avoir les nouvelles lignes en mémoire
            db.session.flush()
            
            # Calculer les totaux via la méthode du modèle
            devis.calculer_totaux()
        
        db.session.commit()
        
        flash(f'Devis {devis.numero} modifié avec succès !', 'success')
        return redirect(url_for('devis_liste'))
    
    # Convertir les lignes en dict pour le JSON
    lignes_dict = []
    for ligne in devis.lignes:
        ligne_data = {
            'tache': ligne.tache,
            'vehicule': ligne.vehicule,
            'description': ligne.description,
            'quantite': ligne.quantite,
            'unite': ligne.unite,
            'prix_unitaire_ht': float(ligne.prix_unitaire_ht),
            'tva_pourcent': float(ligne.tva_pourcent),
            'total_ttc': float(ligne.total_ttc)
        }
        lignes_dict.append(ligne_data)
    
    # Charger les prix pour le formulaire
    prix_catalogue = PrixCatalogue.query.filter_by(actif=True).order_by(PrixCatalogue.categorie, PrixCatalogue.code).all()
    
    return render_template('devis/form.html', 
                         form=form, 
                         title='Éditer le devis',
                         devis=devis,
                         lignes_dict=lignes_dict,
                         prix_catalogue=prix_catalogue)


@app.route('/devis/<int:id>/supprimer', methods=['POST'])
@login_required
def devis_supprimer(id):
    """Supprimer un devis"""
    devis = Devis.query.get_or_404(id)
    numero = devis.numero
    
    db.session.delete(devis)
    db.session.commit()
    
    app.logger.info(f'Devis supprimé: {numero} (ID: {id})')
    flash(f'Devis {numero} supprimé avec succès !', 'success')
    return redirect(url_for('devis_liste'))


@app.route('/api/prix/<code>')
def api_prix_detail(code):
    """API pour récupérer les détails d'un prix"""
    prix = PrixCatalogue.query.filter_by(code=code).first()
    if prix:
        return jsonify({
            'code': prix.code,
            'description': prix.description,
            'prix': prix.prix,
            'categorie': prix.categorie
        })
    return jsonify({'error': 'Prix non trouvé'}), 404


# ========== ROUTES FACTURES ==========

@app.route('/factures')
@login_required
def factures_liste():
    """Liste toutes les factures"""
    search = request.args.get('search', '')
    etat_filter = request.args.get('etat', '')
    
    query = Facture.query
    
    if search:
        query = query.join(Client).filter(
            db.or_(
                Facture.numero.ilike(f'%{search}%'),
                Client.nom.ilike(f'%{search}%')
            )
        )
    
    if etat_filter:
        query = query.filter_by(etat_paiement=etat_filter)
    
    factures = query.order_by(Facture.created_at.desc()).all()
    
    return render_template('factures/liste.html', factures=factures, search=search, etat_filter=etat_filter)


@app.route('/factures/<int:id>')
@login_required
def facture_voir(id):
    """Voir les détails d'une facture"""
    facture = Facture.query.get_or_404(id)
    return render_template('factures/voir.html', facture=facture)


@app.route('/devis/<int:id>/changer-statut', methods=['POST'])
@login_required
def devis_changer_statut(id):
    """Changer le statut d'un devis"""
    devis = Devis.query.get_or_404(id)
    nouveau_statut = request.form.get('statut')
    
    if nouveau_statut in ['brouillon', 'envoye', 'accepte', 'refuse']:
        devis.statut = nouveau_statut
        db.session.commit()
        flash(f'Devis marqué comme "{nouveau_statut}"', 'success')
    else:
        flash('Statut invalide', 'error')
    
    return redirect(url_for('devis_voir', id=id))


@app.route('/devis/<int:devis_id>/convertir-facture', methods=['POST'])
@login_required
def devis_convertir_facture(devis_id):
    """Convertir un devis en facture"""
    devis = Devis.query.get_or_404(devis_id)
    
    # Vérifier si une facture existe déjà pour ce devis
    if devis.facture:
        flash(f'Une facture existe déjà pour ce devis !', 'error')
        return redirect(url_for('devis_voir', id=devis_id))
    
    # Générer le numéro de facture
    derniere_facture = Facture.query.order_by(Facture.id.desc()).first()
    if derniere_facture and derniere_facture.numero:
        try:
            dernier_num = int(derniere_facture.numero)
            nouveau_num = str(dernier_num + 1).zfill(3)
        except (ValueError, AttributeError):
            nouveau_num = "001"
    else:
        nouveau_num = "001"
    
    # Créer la facture
    facture = Facture(
        numero=nouveau_num,
        date=date.today(),
        devis_id=devis.id,
        client_id=devis.client_id,
        montant_ttc=round(devis.total_ttc, 2),
        acompte=round(devis.acompte, 2),
        reste_a_payer=round(devis.total_ttc - devis.acompte, 2),
        etat_paiement='En attente'
    )
    
    # Mettre à jour le statut du devis
    devis.statut = 'accepte'
    
    db.session.add(facture)
    db.session.commit()
    
    app.logger.info(f'Devis {devis.numero} converti en facture {facture.numero} - Montant TTC: {facture.montant_ttc:.2f}€')
    flash(f'Facture {facture.numero} créée avec succès !', 'success')
    return redirect(url_for('facture_voir', id=facture.id))


@app.route('/factures/<int:id>/enregistrer-paiement', methods=['POST'])
@login_required
def facture_enregistrer_paiement(id):
    """Enregistrer un paiement pour une facture"""
    facture = Facture.query.get_or_404(id)
    
    montant = round(float(request.form.get('montant', 0)), 2)
    mode_paiement = request.form.get('mode_paiement', 'Paiement par virement')
    
    if montant <= 0:
        flash('Le montant du paiement doit être supérieur à 0 !', 'error')
        return redirect(url_for('facture_voir', id=id))
    
    # Arrondir les montants pour éviter les problèmes de précision float
    facture.acompte = round(facture.acompte + montant, 2)
    facture.reste_a_payer = round(facture.montant_ttc - facture.acompte, 2)
    
    # Vérifier si la facture est payée (avec une tolérance de 0.01€ pour les erreurs d'arrondi)
    if facture.reste_a_payer <= 0.01:
        facture.etat_paiement = 'Payé'
        facture.mode_paiement = mode_paiement
        facture.date_paiement = date.today()
        facture.reste_a_payer = 0
        flash(f'Facture {facture.numero} payée intégralement par {mode_paiement.lower()} !', 'success')
    else:
        facture.etat_paiement = 'Paiement partiel'
        flash(f'Paiement de {montant:.2f} € enregistré. Reste à payer : {facture.reste_a_payer:.2f} €', 'success')
    
    db.session.commit()
    
    # Log du paiement
    if facture.etat_paiement == 'Payé':
        app.logger.info(f'Facture {facture.numero} payée intégralement - Montant: {facture.montant_ttc:.2f}€ - Mode: {mode_paiement}')
    else:
        app.logger.info(f'Paiement partiel facture {facture.numero} - Montant reçu: {montant:.2f}€ - Reste: {facture.reste_a_payer:.2f}€')
    
    return redirect(url_for('facture_voir', id=id))


@app.route('/factures/<int:id>/supprimer', methods=['POST'])
@login_required
def facture_supprimer(id):
    """Supprimer une facture"""
    facture = Facture.query.get_or_404(id)
    numero = facture.numero
    montant = facture.montant_ttc
    etat = facture.etat_paiement
    
    db.session.delete(facture)
    db.session.commit()
    
    app.logger.warning(f'Facture supprimée: {numero} (ID: {id}) - Montant TTC: {montant:.2f}€ - État: {etat}')
    flash(f'Facture {numero} supprimée avec succès !', 'success')
    return redirect(url_for('factures_liste'))


# ===========================
# Routes PDF
# ===========================

@app.route('/devis/<int:id>/pdf')
@login_required
def devis_pdf(id):
    """Générer le PDF d'un devis"""
    from xhtml2pdf import pisa
    from io import BytesIO
    from datetime import timedelta
    
    devis = Devis.query.get_or_404(id)
    config = Config.query.first()
    
    # Rendre le template HTML
    html_content = render_template('pdf/devis.html', devis=devis, config=config, timedelta=timedelta)
    
    # Générer le PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        return "Erreur lors de la génération du PDF", 500
    
    # Créer la réponse
    pdf_buffer.seek(0)
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Devis_{devis.numero}.pdf'
    
    return response


@app.route('/factures/<int:id>/pdf')
@login_required
def facture_pdf(id):
    """Générer le PDF d'une facture"""
    from xhtml2pdf import pisa
    from io import BytesIO
    
    facture = Facture.query.get_or_404(id)
    config = Config.query.first()
    
    # Rendre le template HTML
    html_content = render_template('pdf/facture.html', facture=facture, config=config)
    
    # Générer le PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)
    
    if pisa_status.err:
        return "Erreur lors de la génération du PDF", 500
    
    # Créer la réponse
    pdf_buffer.seek(0)
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Facture_{facture.numero}.pdf'
    
    return response
