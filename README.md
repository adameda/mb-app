# Devis App - Gestion de Devis et Factures

Application Flask moderne pour remplacer le système Excel de gestion de devis et factures.

## Installation

```bash
# Installer UV si nécessaire
pip install uv

# Installer les dépendances
uv sync

# Lancer l'application
uv run python run.py
```

## Fonctionnalités

- ✅ Gestion des clients
- ✅ Catalogue de prix
- ✅ Création de devis
- ✅ Génération de PDF
- ✅ Suivi des factures et paiements
- ✅ Interface moderne et responsive

## Structure

```
devis-app/
├── app/                  # Application Flask
│   ├── models.py        # Modèles de base de données
│   ├── routes.py        # Routes et vues
│   ├── forms.py         # Formulaires WTForms
│   ├── templates/       # Templates HTML
│   └── static/          # CSS, JS, images
├── instance/            # Base de données (généré)
├── pyproject.toml       # Dépendances UV
└── run.py              # Point d'entrée
```
