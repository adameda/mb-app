#!/bin/sh
set -e

# Utiliser le PORT de Railway ou 5000 par défaut
PORT="${PORT:-5000}"

# Lancer Gunicorn avec exec pour recevoir les signaux proprement
exec gunicorn --bind "0.0.0.0:${PORT}" --workers 2 run:app
