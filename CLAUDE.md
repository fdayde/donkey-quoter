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
├── src/donkey_quoter/       # Main package
│   ├── models.py           # Pydantic models (Quote)
│   ├── quote_manager.py    # Quote business logic
│   ├── haiku_generator.py  # Haiku generation
│   ├── ui_components.py    # Reusable UI components
│   ├── translations.py     # i18n FR/EN
│   ├── state_manager.py    # Streamlit session state
│   └── styles.css         # Custom CSS
└── data/quotes.py          # Quote database
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
2. Haiku generation from quotes
3. Favorites management with JSON export
4. Bilingual interface (FR/EN)

## Common Tasks

### Add New Quotes
Edit `src/donkey_quoter/data/quotes.py`:
```python
Quote(
    id="custom_001",
    text={"fr": "Citation française", "en": "English quote"},
    author={"fr": "Auteur", "en": "Author"},
    category="personal"
)
```

### Modify UI Theme
- Colors: Edit `src/donkey_quoter/styles.css`
- Layout: Modify `ui_components.py`
- Streamlit theme: `.streamlit/config.toml`

### Add New Language
1. Update `translations.py` with new language
2. Add translations to all Quote objects
3. Update language selector in `app.py`

## Git Workflow
- Branch: `feature/improvements`
- Main branch: `main`
- Follow conventional commits
- Run formatters before commit

## Important Notes
- No package.json (pure Python project)
- No automated tests yet implemented
- Pre-commit hooks configured with Ruff
- Apache 2.0 License (note: pyproject.toml says MIT - needs alignment)
