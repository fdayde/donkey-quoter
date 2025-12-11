# CLAUDE.md - Donkey Quoter Project Assistant Guide

## Project Overview
Donkey Quoter est une application web Streamlit pour découvrir des citations inspirantes et générer des haïkus poétiques. Projet Python 3.9+ utilisant Streamlit, avec interface bilingue FR/EN.

## Quick Commands

### Development
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run application
streamlit run app.py

# Code formatting and linting
ruff check src/ --fix
ruff format src/

# Pre-commit setup
pre-commit install
pre-commit run --all-files
```

### Haiku Management CLI
```bash
# CLI unifié - mode batch bilingue automatique (FR + EN simultanément)

# Générer les haïkus manquants
python scripts/haiku_cli.py generate

# Régénérer tous les haïkus
python scripts/haiku_cli.py generate --all

# Avec limite et simulation
python scripts/haiku_cli.py --dry-run generate --limit 10

# Statistiques
python scripts/haiku_cli.py stats

# Export (JSON/CSV)
python scripts/haiku_cli.py export --format csv
```

### Testing
```bash
# Run tests (when implemented)
pytest
pytest --cov=src
```

## Project Structure
```
donkey-quoter/
├── app.py                    # Streamlit entry point
├── api.py                    # FastAPI entry point
├── Dockerfile                # Docker config for API deployment
├── render.yaml               # Render deployment config
├── src/donkey_quoter/        # Main package
│   ├── core/                 # Business logic
│   │   ├── models.py         # Pydantic models (Quote)
│   │   ├── services.py       # Unified service (DonkeyQuoterService)
│   │   ├── quote_adapter.py  # Quote adapter for Streamlit
│   │   ├── haiku_adapter.py  # Haiku adapter for Streamlit
│   │   └── storage.py        # Haiku persistence (JSON)
│   ├── api/                  # REST API module
│   │   ├── routers/          # API endpoints (quotes, haikus, export)
│   │   ├── auth.py           # API key auth & rate limiting
│   │   └── client.py         # HTTP client for Streamlit
│   ├── infrastructure/       # External integrations
│   │   └── anthropic_client.py  # Claude API client
│   ├── ui/                   # Streamlit UI components
│   │   ├── components.py     # Reusable UI components
│   │   └── styles.css        # Custom CSS
│   ├── config/settings.py    # App settings
│   ├── translations.py       # i18n FR/EN
│   ├── state_manager.py      # Streamlit session state
│   └── data/quotes.json      # Quote database (JSON)
├── scripts/haiku_cli.py      # CLI for batch haiku generation
└── data/haikus.json          # Generated haikus storage
```

## Key Technical Details

### Code Style
- Ruff for formatting, linting, and import sorting (line-length: 88)
- Type hints avec Pydantic

### Architecture Patterns
- MVC-like separation (models, business logic, UI)
- Pydantic for data validation
- Session state management centralisé
- CSS personnalisé pour theming amber/stone

### Main Features
1. Quote discovery (classic, personal, humorous)
2. Haiku generation from quotes (Claude API)
3. Bilingual interface (FR/EN)
4. REST API (FastAPI) for backend separation

## Common Tasks

### Add New Quotes
Edit `src/donkey_quoter/data/quotes.json`:
```json
{
    "id": "custom_001",
    "text": {"fr": "Citation française", "en": "English quote"},
    "author": {"fr": "Auteur", "en": "Author"},
    "category": "personal"
}
```

### Modify UI Theme
- Colors: Edit `src/donkey_quoter/ui/styles.css`
- Layout: Modify `src/donkey_quoter/ui/components.py`
- Streamlit theme: `.streamlit/config.toml`

### Add New Language
1. Update `translations.py` with new language
2. Add translations to all Quote objects
3. Update language selector in `app.py`

## Git Workflow
- Main branch: `main`
- Follow conventional commits
- Run formatters before commit

## Important Notes
- No package.json (pure Python project)
- No automated tests yet implemented
- Pre-commit hooks configured with Ruff
- Apache 2.0 License (note: pyproject.toml says MIT - needs alignment)
