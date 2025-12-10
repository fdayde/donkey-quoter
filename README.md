# Donkey Quoter

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

🫏 *Wisdom & Poetry* - An elegant web application to discover inspiring quotes and generate poetic haikus.

💡 **Want to contribute quotes?** Check out our [Quote Submission Guide](#-suggest-new--quotes)

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
- **fastapi** >= 0.109.0: REST API framework
- **uvicorn** >= 0.27.0: ASGI server
- **httpx** >= 0.27.0: HTTP client
- **python-dotenv**: Environment variables management
- **python** >= 3.9: Required Python version

## 🎮 Usage

### Streamlit App (default)

```bash
# Launch the application
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🔌 REST API

Donkey Quoter includes a full REST API built with FastAPI, enabling programmatic access to quotes and haiku generation.

### Quick Start

```bash
# Start the API server
uvicorn api:app --port 8001

# Or with auto-reload for development
uvicorn api:app --reload --port 8001
```

Access the interactive documentation at:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/quotes` | List all quotes (with pagination) | No |
| `GET` | `/quotes/random` | Get a random quote | No |
| `GET` | `/quotes/{id}` | Get a specific quote | No |
| `POST` | `/quotes` | Create a new quote | No |
| `GET` | `/haikus/{quote_id}` | Get stored haiku for a quote | No |
| `GET` | `/haikus/{quote_id}/exists` | Check if haiku exists | No |
| `POST` | `/haikus/generate` | Generate a new haiku | **Yes** |
| `GET` | `/haikus/rate-limit` | Check rate limit status | No |
| `GET` | `/export` | Export all data | No |
| `GET` | `/export/download` | Download data as JSON file | No |

### Authentication (API Key)

Haiku generation requires an API key for rate limiting. Add the key in the `X-API-Key` header.

**Setup:**

1. Generate a secure API key (any string you choose)
2. Add it to your `.env` file:
   ```env
   DONKEY_QUOTER_API_KEY=your-secret-api-key
   ```
3. Use it in requests:
   ```bash
   curl -X POST http://localhost:8001/haikus/generate \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-api-key" \
     -d '{"quote_id": "c01", "force_new": true}'
   ```

**Multiple API keys** (optional):
```env
DONKEY_QUOTER_API_KEYS=key1,key2,key3
```

**Development mode** (adds a test key `dev-key-for-testing`):
```env
DONKEY_QUOTER_DEV_MODE=true
```

### Rate Limiting

- **Limit**: 5 haiku generations per API key per 24 hours
- Check status: `GET /haikus/rate-limit`
- Response headers include `X-RateLimit-Remaining`

### Query Parameters

**Language** (all endpoints):
- Query param: `?lang=fr` or `?lang=en`
- Header: `Accept-Language: fr` or `Accept-Language: en`
- Default: `fr`

**Pagination** (`GET /quotes`):
- `?limit=50` (max 100)
- `?offset=0`

**Filtering** (`GET /quotes`, `GET /quotes/random`):
- `?category=classic|personal|humor|poem`
- `?type=preset|user|generated`

### Example Requests

```bash
# Get a random quote in English
curl "http://localhost:8001/quotes/random?lang=en"

# List quotes with pagination
curl "http://localhost:8001/quotes?limit=10&offset=0&category=classic"

# Check if haiku exists
curl "http://localhost:8001/haikus/c01/exists?lang=fr"

# Generate haiku (requires API key)
curl -X POST "http://localhost:8001/haikus/generate?lang=fr" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"quote_id": "c01", "force_new": false}'

# Export all data
curl "http://localhost:8001/export"
```

### Python Client Example

```python
import httpx

client = httpx.Client(
    base_url="http://localhost:8001",
    headers={"X-API-Key": "your-api-key"}
)

# Get random quote
quote = client.get("/quotes/random?lang=fr").json()
print(quote["data"]["text"]["fr"])

# Generate haiku
response = client.post("/haikus/generate", json={
    "quote_id": quote["data"]["id"],
    "force_new": True
})
print(response.json()["haiku_text"])
```

### Running Streamlit with API Backend

You can configure Streamlit to use the REST API instead of direct service calls:

1. Start the API:
   ```bash
   uvicorn api:app --port 8001
   ```

2. Configure Streamlit to use the API (in `.env`):
   ```env
   USE_API_BACKEND=true
   API_BASE_URL=http://localhost:8001
   DONKEY_QUOTER_API_KEY=your-api-key
   ```

3. Start Streamlit:
   ```bash
   streamlit run app.py
   ```

This enables a true frontend/backend separation, useful for:
- Scaling the API independently
- Using the same API for multiple clients (web, mobile, CLI)
- Deploying frontend and backend on different services

## 🛠️ Project Structure

```
donkey-quoter/
├── app.py                  # Streamlit entry point
├── api.py                  # FastAPI entry point
├── src/donkey_quoter/      # Main package
│   ├── core/              # Business logic
│   │   ├── models.py      # Data models (Quote, QuoteInput)
│   │   ├── services.py    # Unified service (DonkeyQuoterService)
│   │   ├── quote_adapter.py   # Quote adapter for Streamlit
│   │   ├── haiku_adapter.py   # Haiku adapter for Streamlit
│   │   ├── storage.py     # Haiku persistence (JSON)
│   │   └── data_loader.py # Quote loading
│   ├── api/               # REST API module
│   │   ├── __init__.py    # FastAPI app factory
│   │   ├── schemas.py     # Request/Response models
│   │   ├── dependencies.py # Dependency injection
│   │   ├── auth.py        # API key auth & rate limiting
│   │   ├── client.py      # HTTP client for Streamlit
│   │   └── routers/       # API endpoints
│   │       ├── quotes.py  # /quotes endpoints
│   │       ├── haikus.py  # /haikus endpoints
│   │       └── export.py  # /export endpoints
│   ├── infrastructure/    # External integrations
│   │   └── anthropic_client.py # Claude API client
│   ├── ui/                # Streamlit UI components
│   │   └── components.py  # Reusable UI components
│   ├── config/            # Configuration modules
│   │   └── settings.py    # App settings
│   ├── data/
│   │   └── quotes.json    # Quote database
│   ├── translations.py    # FR/EN translations
│   └── state_manager.py   # Session state management
├── scripts/
│   └── haiku_cli.py       # CLI for batch haiku generation
├── data/
│   └── haikus.json        # Generated haikus storage
└── tests/                 # Test suite
```

## 🎨 Customization

### Adding Quotes

#### 💡 Suggest New 🫏 Quotes
We encourage community contributions to enrich our quote collection! You can suggest quotes in two ways:

**📝 Submit via GitHub Issue (Recommended)**
The easiest way to contribute quotes is through our dedicated template:
1. Go to [Submit a Quote](https://github.com/fdayde/donkey-quoter/issues/new?template=quote_submission.yml)
2. Fill in the form with your quote in both French and English
3. Select the appropriate category (classic, personal, humorous)
4. Submit and wait for review

**⚡ Local Development**
For testing purposes, you can modify the `src/donkey_quoter/data/quotes.py` file directly:

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

*Local Development*:
1. Create a `.env` file in the project root
2. Add your Anthropic API key: `ANTHROPIC_API_KEY=your_key_here`
3. Optionally set the model: `CLAUDE_MODEL=claude-3-5-haiku-20241022`

*Streamlit Cloud Deployment*:
1. Deploy your app to Streamlit Cloud
2. Go to your app's Settings → Secrets
3. Add your secrets in TOML format:
   ```toml
   ANTHROPIC_API_KEY = "your_key_here"
   CLAUDE_MODEL = "claude-3-haiku-20240307"
   ```
4. Save and restart your app
5. **Note**: The app automatically uses Streamlit secrets when available, falling back to `.env` for local development

**Haiku Generation CLI**:
```bash
# CLI unifié pour la gestion des haïkus (mode batch bilingue optimisé)

# Voir l'aide
python scripts/haiku_cli.py --help

# Générer les haïkus manquants (FR + EN simultanément)
python scripts/haiku_cli.py generate

# Régénérer tous les haïkus
python scripts/haiku_cli.py generate --all

# Limiter le nombre de citations
python scripts/haiku_cli.py generate --limit 10

# Simulation sans appel API
python scripts/haiku_cli.py --dry-run generate --all --limit 3

# Génération silencieuse (pas de confirmation)
python scripts/haiku_cli.py generate --all -y

# Statistiques complètes
python scripts/haiku_cli.py stats

# Export des données (JSON ou CSV)
python scripts/haiku_cli.py export --format csv --output mes_haikus.csv
```

**Key Features**:
- **Batch processing**: Generate FR + EN haikus simultaneously (2x more efficient)
- **Smart detection**: Only generates missing haikus by default
- **Cost estimation**: Shows API usage cost before generation
- **Progress tracking**: Real-time progress bar with batch status
- **Flexible export**: JSON and CSV formats supported
- **Dry-run mode**: Test without API calls
- **Metadata storage**: Haikus saved with generation date and model info
- Fallback to stored haikus when API unavailable

## 🏷️ Versioning

Version is managed in `src/donkey_quoter/__init__.py`. To release:
```bash
# Update version
__version__ = "1.2.0"

# Tag and push
git tag v1.2.0 && git push --tags
```

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
