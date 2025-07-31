# Donkey Quoter

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

🫏 *Wisdom & Poetry* - An elegant web application to discover inspiring quotes and generate poetic haikus.

## ✨ Overview

Donkey Quoter is a minimalist web application that allows you to:
- 🎲 Discover random quotes (classic, humorous, personal)
- ✨ Generate poetic haikus inspired by quotes
- 💾 Save your favorite quotes and haikus
- 📥 Export your collection in JSON format
- 🌐 Switch between French and English

## 📸 Screenshots

<div align="center">

![App](docs/app.png)

</div>

## 🎯 Features

### Diverse Quotes
- **Classic**: Proverbs and popular wisdom
- **Personal**: Original philosophical reflections
- **Humorous**: Light and amusing quotes

### Haiku Generator
Automatic creation of thematic haikus based on the spirit of the displayed quote.

### Elegant Interface
- Minimalist design with amber/stone color palette
- Modern and readable sans-serif font
- Smooth animations and responsive interface

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/donkey-quoter.git
cd donkey-quoter

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## 📦 Dependencies

- **streamlit** >= 1.32.0: Web application framework
- **pydantic** >= 2.0.0: Data validation
- **python** >= 3.9: Required Python version

## 🎮 Usage

```bash
# Launch the application
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

## 🛠️ Project Structure

```
donkey-quoter/
├── app.py                  # Main entry point
├── src/donkey_quoter/      # Main package
│   ├── models.py          # Data models (Quote)
│   ├── quote_manager.py   # Quote management
│   ├── haiku_generator.py # Haiku generator
│   ├── ui_components.py   # Reusable UI components
│   ├── translations.py    # FR/EN translations
│   └── styles.css        # Custom styles
├── .streamlit/
│   └── config.toml       # Theme configuration
└── data/
    └── quotes.json       # Quote database
```

## 🎨 Customization

### Adding Quotes

#### Submit via GitHub Issue
The easiest way to contribute quotes is through our GitHub issue template:
1. Go to [Submit a Quote](https://github.com/fdayde/donkey-quoter/issues/new?template=quote_submission.yml)
2. Fill in the form with your quote in both languages
3. Submit and wait for review

#### Local Development
For testing, you can modify the `src/donkey_quoter/data/quotes.py` file directly:

```python
Quote(
  id="custom_001",
  text={
    "fr": "Votre citation en français",
    "en": "Your quote in English"
  },
  author={
    "fr": "Auteur",
    "en": "Author"
  },
  category="personal"
)
```

### Generating Haikus

The application can generate haikus using Claude API. To regenerate haikus in batch:

```bash
# Generate missing haikus only
python scripts/regenerate_haikus.py

# Force regeneration of all haikus
python scripts/regenerate_haikus.py --regenerate-all

# Test with a limited number of quotes
python scripts/regenerate_haikus.py --limit 5 --dry-run
```

**Requirements**:
- Set `ANTHROPIC_API_KEY` in your `.env` file
- Haikus are stored with metadata (date, model) in `data/haikus.json`

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Development setup
- Code style and quality standards
- Submitting pull requests
- Running tests

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by popular wisdom and the love of simple 🫏 poetry.

---

*"The patient donkey carries heavy wisdom, slow but steady steps"* 🫏
