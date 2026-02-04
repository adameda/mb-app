# 📊 MB App - Gestion de Devis et Factures

Application web Flask moderne pour la gestion complète de devis et factures, remplaçant les fichiers Excel traditionnels.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Railway](https://img.shields.io/badge/Railway-Deployed-success.svg)

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Technologies](#-technologies)
- [Installation locale](#-installation-locale)
- [Utilisation](#-utilisation)
- [Déploiement](#-déploiement)
- [Structure du projet](#-structure-du-projet)
- [Workflow de développement](#-workflow-de-développement)
- [Variables d'environnement](#-variables-denvironnement)
- [Sécurité](#-sécurité)

---

## ✨ Fonctionnalités

### Gestion Clients
- ✅ Création et modification de clients
- ✅ Stockage des informations (nom, adresse, SIRET, TVA)
- ✅ Liste consultable et recherche

### Catalogue de Prix
- ✅ Gestion du catalogue de produits/services
- ✅ Prix unitaires configurables
- ✅ Descriptions détaillées

### Devis
- ✅ Création de devis multi-lignes
- ✅ Calcul automatique HT/TTC avec TVA
- ✅ Export PDF professionnel
- ✅ Suivi de l'état (brouillon, envoyé, accepté, refusé)
- ✅ Conversion devis → facture en un clic

### Factures
- ✅ Génération depuis devis ou création manuelle
- ✅ Numérotation automatique
- ✅ Suivi des paiements (total, partiel, impayé)
- ✅ Export PDF personnalisé
- ✅ Gestion des échéances

### Sécurité & Authentification
- ✅ Authentification obligatoire (Flask-Login)
- ✅ Protection CSRF sur tous les formulaires
- ✅ Logging des actions critiques
- ✅ Pages d'erreur personnalisées (404, 403, 500)
- ✅ Sessions sécurisées (HttpOnly, SameSite)

---

## 🛠️ Technologies

### Backend
- **Python 3.11+** - Langage principal
- **Flask 3.0+** - Framework web
- **SQLAlchemy** - ORM pour base de données
- **Flask-Login** - Gestion authentification
- **Flask-WTF** - Formulaires et validation

### Frontend
- **Tailwind CSS** - Framework CSS moderne
- **HTML5/Jinja2** - Templates dynamiques
- **JavaScript** - Interactions client

### Base de données
- **SQLite** - Développement local
- **PostgreSQL 15** - Production (Railway)

### PDF & Export
- **WeasyPrint** - Génération PDF avancée
- **xhtml2pdf** - Alternative PDF

### Déploiement
- **Docker** - Conteneurisation
- **Railway** - Plateforme de déploiement
- **Gunicorn** - Serveur WSGI production
- **uv** - Gestionnaire de paquets Python moderne

---

## 🚀 Installation locale

### Prérequis

```bash
# Python 3.11 ou supérieur
python --version

# uv (gestionnaire de paquets moderne)
pip install uv
```

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/adameda/mb-app.git
cd mb-app

# 2. Installer les dépendances
uv sync

# 3. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 4. Générer une clé secrète
python -c "import secrets; print(secrets.token_hex(32))"
# Copier dans SECRET_KEY du fichier .env

# 5. Générer le hash du mot de passe admin
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('votre_mot_de_passe'))"
# Copier dans ADMIN_PASSWORD_HASH du fichier .env

# 6. Initialiser la base de données
python run.py
# Les tables seront créées automatiquement au premier lancement
```

---

## 💻 Utilisation

### Démarrage en local

```bash
# Mode développement (SQLite)
python run.py

# Accéder à l'application
# http://localhost:5000
```

### Test avec Docker (optionnel)

```bash
# Build l'image Docker
docker build -t devis-app .

# Lancer avec docker-compose (PostgreSQL inclus)
docker-compose up

# Accéder à l'application
# http://localhost:5000
```

### Connexion

```
URL: http://localhost:5000
Username: (voir ADMIN_USERNAME dans .env)
Password: (le mot de passe choisi avant le hash)
```

---

## 🌐 Déploiement

### Railway (Production)

**L'application est automatiquement déployée sur Railway à chaque push sur `main`.**

#### Configuration Railway

1. **Service PostgreSQL** - Base de données production
2. **Service Web** - Application Flask
3. **Variables d'environnement** configurées :
   - `SECRET_KEY` - Clé secrète Flask
   - `DATABASE_URL` - URL PostgreSQL (auto-injecté)
   - `ADMIN_USERNAME` - Nom d'utilisateur admin
   - `ADMIN_PASSWORD_HASH` - Hash du mot de passe
   - `PORT` - Port dynamique (auto-injecté)

#### Déploiement automatique

```bash
# Commit et push sur main
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main

# Railway détecte le push et redéploie automatiquement
# Build: ~2-5 minutes
# URL: https://mb-app-production.up.railway.app
```

#### Optimisation des builds

Le fichier `.railwayignore` évite les builds inutiles :
- ❌ Pas de build pour README.md
- ❌ Pas de build pour docker-compose.yml
- ✅ Build uniquement pour changements de code

---

## 📁 Structure du projet

```
devis-app/
├── app/                           # Application Flask
│   ├── __init__.py               # Factory + config Flask-Login
│   ├── models.py                 # Modèles SQLAlchemy (Client, Devis, Facture...)
│   ├── routes.py                 # Routes et logique métier
│   ├── forms.py                  # Formulaires WTForms
│   ├── config.py                 # Configuration (DB, sessions, sécurité)
│   ├── auth.py                   # Authentification utilisateur
│   ├── errors.py                 # Gestionnaires d'erreurs
│   ├── templates/                # Templates Jinja2
│   │   ├── base.html            # Template de base
│   │   ├── login.html           # Page de connexion
│   │   ├── index.html           # Dashboard
│   │   ├── clients/             # Templates clients
│   │   ├── devis/               # Templates devis
│   │   ├── factures/            # Templates factures
│   │   ├── prix/                # Templates catalogue
│   │   ├── pdf/                 # Templates PDF
│   │   └── errors/              # Pages d'erreur (404, 403, 500)
│   └── static/                   # Ressources statiques
│       ├── css/                 # Tailwind CSS
│       ├── js/                  # JavaScript
│       └── images/              # Images et logos
├── instance/                      # Base de données locale (généré)
│   ├── devis.db                 # SQLite (dev)
│   └── pdfs/                    # PDFs générés
├── logs/                          # Logs de l'application (généré)
│   └── app.log                  # Fichier de logs rotatif
├── context_files/                 # Fichiers de référence
│   └── devis_auto.xlsm          # Ancien fichier Excel
├── .env                          # Variables d'environnement (local)
├── .env.example                  # Template variables d'environnement
├── .gitignore                    # Fichiers Git ignorés
├── .dockerignore                 # Fichiers Docker ignorés
├── .railwayignore                # Fichiers Railway ignorés
├── Dockerfile                    # Configuration Docker
├── docker-compose.yml            # Orchestration Docker (local)
├── railway.json                  # Configuration Railway
├── pyproject.toml                # Dépendances et config Python (uv)
├── uv.lock                       # Lock file dépendances
├── run.py                        # Point d'entrée de l'application
└── README.md                     # Documentation (ce fichier)
```

---

## 🔄 Workflow de développement

### Branches

```
main (production)
├── Déployée automatiquement sur Railway
├── Toujours stable et testée
└── Protégée

dev (développement)
├── Branche de travail quotidienne
├── Tests en local avant merge
└── Merge dans main pour déployer
```

### Workflow quotidien

```bash
# 1. Travailler sur dev
git checkout dev
git pull origin dev

# 2. Développer et tester en local
python run.py
# ... coder, tester ...

# 3. Commit avec convention
git add .
git commit -m "feat(devis): ajouter export Excel"

# 4. Push sur dev
git push origin dev

# 5. Tester avec Docker (optionnel)
docker-compose up

# 6. Quand stable, merger dans main
git checkout main
git pull origin main
git merge dev
git push origin main

# Railway déploie automatiquement ! 🚀
```

### Convention de commits

```
feat(scope):     Nouvelle fonctionnalité
fix(scope):      Correction de bug
docs:            Documentation
refactor(scope): Refactoring code
chore:           Tâches diverses (deps, config...)
style:           Formatage code
perf(scope):     Optimisation performance
```

**Exemples :**
```bash
git commit -m "feat(devis): ajouter export Excel"
git commit -m "fix(facture): corriger calcul TVA 20%"
git commit -m "docs: mettre à jour README déploiement"
git commit -m "refactor(pdf): optimiser génération PDF"
```

---

## 🔐 Variables d'environnement

### Fichier `.env` (local)

```bash
# Flask
SECRET_KEY=votre_cle_secrete_64_caracteres_minimum
FLASK_ENV=development
FLASK_DEBUG=True

# Base de données (local = SQLite, prod = PostgreSQL auto-injecté)
DATABASE_URL=sqlite:///devis.db

# Authentification
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=scrypt:32768:8:1$...votre_hash

# Email (optionnel)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=votre_email@gmail.com
MAIL_PASSWORD=votre_mot_de_passe_app
MAIL_DEFAULT_SENDER=votre_email@gmail.com
```

### Railway (production)

Variables configurées dans l'interface Railway :
- `SECRET_KEY` - Généré avec `secrets.token_hex(32)`
- `DATABASE_URL` - Auto-injecté par Railway (PostgreSQL)
- `ADMIN_USERNAME` - Login admin
- `ADMIN_PASSWORD_HASH` - Hash généré avec werkzeug
- `PORT` - Auto-injecté par Railway
- `RAILWAY_ENVIRONMENT` - Auto-injecté (détection production)

---

## 🔒 Sécurité

### Mesures implémentées

#### Authentification
- ✅ Connexion obligatoire pour toutes les routes (sauf login)
- ✅ Hash bcrypt des mots de passe (werkzeug.security)
- ✅ Sessions sécurisées avec timeout (1 heure)

#### Protection des formulaires
- ✅ Protection CSRF (Flask-WTF)
- ✅ Validation des données serveur + client
- ✅ Limitation de taille des requêtes (16MB max)

#### Cookies et sessions
- ✅ `SESSION_COOKIE_HTTPONLY=True` (anti-XSS)
- ✅ `SESSION_COOKIE_SAMESITE='Lax'` (anti-CSRF)
- ✅ `SESSION_COOKIE_SECURE=True` en production (HTTPS only)
- ✅ Expiration automatique après 1 heure

#### Logging
- ✅ Logging de toutes les actions critiques
- ✅ Fichiers logs rotatifs (10KB max, 10 backups)
- ✅ Logs désactivés en mode DEBUG (évite pollution)

#### Erreurs
- ✅ Pages d'erreur personnalisées (404, 403, 500)
- ✅ Pas de stacktraces exposées en production
- ✅ Rollback DB automatique sur erreur 500

#### Base de données
- ✅ PostgreSQL en production (plus robuste que SQLite)
- ✅ Connexion via URL sécurisée (Railway)
- ✅ Migrations gérées par SQLAlchemy

---

## 📝 Licence

Ce projet est privé et destiné à un usage interne.

---

## 👨‍💻 Auteur

**Adam HALLADJA**  
Data Scientist - AI Engineer

---

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs : `logs/app.log` (local) ou Railway Dashboard (prod)
2. Consulter cette documentation
3. Vérifier les variables d'environnement

---

**Version actuelle :** v0.1.0  
**Dernière mise à jour :** 2026-02-04  
**Statut :** ✅ En production sur Railway
