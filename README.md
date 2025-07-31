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

### AI-Powered Haiku Generator
- **Claude Haiku 3.5**: Generate personalized haikus inspired by quotes using Anthropic's latest model
- **Real-time generation**: Create new haikus with one click with Claude Haiku 3 (5 generations per session)
- **Multi-language support**: Available in both French and English
- **Stored haikus**: Access pre-generated haikus when API is unavailable

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

- **streamlit** >= 1.31.0: Web application framework
- **pydantic** >= 2.5.0: Data validation and models
- **anthropic** >= 0.18.0: Claude API integration for haiku generation
- **python-dotenv**: Environment variables management
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
│   ├── haiku_generator.py # AI haiku generation
│   ├── haiku_storage.py   # Haiku persistence
│   ├── claude_api.py      # Claude API integration
│   ├── ui_components.py   # Reusable UI components
│   ├── translations.py    # FR/EN translations
│   ├── state_manager.py   # Session state management
│   ├── config/            # Configuration modules
│   │   ├── model_mapping.py # Claude model mappings
│   │   └── api_pricing.py   # API pricing config
│   ├── data/
│   │   └── quotes.py      # Quote database
│   └── styles.css        # Custom styles
├── scripts/
│   ├── regenerate_haikus.py    # Batch haiku generation
│   └── generate_missing_haikus.py # Generate missing haikus
├── data/
│   └── haikus.json       # Generated haikus storage
└── tests/                # Test suite
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

### AI Haiku Configuration

The application supports multiple Claude models for haiku generation:

**Supported Models**:
- `claude-3-5-haiku-20241022` (Claude Haiku 3.5) - Latest and fastest
- `claude-3-haiku-20240307` (Claude Haiku 3) - Previous version

**Setup**:
1. Create a `.env` file in the project root
2. Add your Anthropic API key: `ANTHROPIC_API_KEY=your_key_here`
3. Optionally set the model: `CLAUDE_MODEL=claude-3-5-haiku-20241022`

**Batch Generation**:
```bash
# Generate missing haikus only
python scripts/regenerate_haikus.py

# Force regeneration of all haikus
python scripts/regenerate_haikus.py --regenerate-all

# Test with a limited number of quotes
python scripts/regenerate_haikus.py --limit 5 --dry-run
```

**Features**:
- Haikus stored with metadata (date, model) in `data/haikus.json`
- Real-time generation limited to 5 per session
- Fallback to stored haikus when API unavailable

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
