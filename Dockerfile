# Dockerfile pour Donkey Quoter API
# Utilise uv pour une installation rapide et reproductible

FROM python:3.13-slim

# Installer uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY pyproject.toml uv.lock ./

# Installer les dépendances (sans le projet lui-même)
RUN uv sync --frozen --no-install-project

# Copier le code source
COPY src/ ./src/
COPY api.py ./
COPY data/ ./data/

# Installer le projet
RUN uv sync --frozen

# Exposer le port
EXPOSE 8001

# Variables d'environnement par défaut
ENV PYTHONUNBUFFERED=1
ENV PORT=8001

# Lancer l'API avec uvicorn (PORT est défini par Render)
CMD uv run uvicorn api:app --host 0.0.0.0 --port ${PORT:-8001}
