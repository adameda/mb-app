# Image de base Python 3.11
FROM python:3.11-slim

# Copier uv depuis l'image officielle
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Installer les dépendances système nécessaires pour pycairo et autres
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY pyproject.toml uv.lock ./

# Installer les dépendances avec uv (sans installer le projet)
RUN uv sync --frozen --no-install-project --no-dev

# Copier tout le code de l'application
COPY . .

# Installer le projet
RUN uv sync --frozen --no-dev

# Définir le PATH pour utiliser le venv
ENV PATH="/app/.venv/bin:$PATH"

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]