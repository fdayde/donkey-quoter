# 🫏 Donkey Quoter

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

> *Wisdom & Poetry* - An elegant web application to discover inspiring quotes and generate poetic haikus.

## ✨ Overview

Donkey Quoter is a minimalist web application that allows you to:
- 🎲 Discover random quotes (classic, humorous, personal)
- ✨ Generate poetic haikus inspired by quotes
- 💾 Save your favorite quotes and haikus
- 📥 Export your collection in JSON format
- 🌐 Switch between French and English

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
- **python** >= 3.10: Required Python version

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
Modify the `data/quotes.json` file to add your own quotes:

```json
{
  "id": "custom_001",
  "text": {
    "fr": "Votre citation en français",
    "en": "Your quote in English"
  },
  "author": {
    "fr": "Auteur",
    "en": "Author"
  },
  "category": "personal"
}
```

### Modifying the Theme
Adjust colors in `.streamlit/config.toml` to customize the appearance.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Add quotes
- 🌍 Improve translations

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Inspired by popular wisdom and the love of simple poetry.

---

*"The patient donkey carries heavy wisdom, slow but steady steps"* 🫏