# Déploiement sur Render

Ce guide explique comment déployer Donkey Quoter sur [Render](https://render.com) avec une architecture API + Frontend séparés.

## Architecture

```
┌─────────────────────────┐     ┌─────────────────────────┐
│   donkey-quoter-app     │     │   donkey-quoter-api     │
│   (Streamlit Frontend)  │────►│   (FastAPI Backend)     │
│   Port: $PORT           │HTTP │   Port: $PORT           │
└─────────────────────────┘     └─────────────────────────┘
```

- **API** : FastAPI, gère les données et la génération de haïkus
- **Frontend** : Streamlit, interface utilisateur

---

## Prérequis

- Compte [Render](https://render.com)
- Repository GitHub connecté à Render
- Clé API Anthropic ([console.anthropic.com](https://console.anthropic.com))

---

## Service 1 : API FastAPI

### Création

1. **Dashboard Render** → **New** → **Web Service**
2. Connecter le repository `donkey-quoter`
3. Sélectionner la branche `feature/api-rest` (ou `main` après merge)

### Configuration

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `donkey-quoter-api` |
| **Runtime** | `Docker` |
| **Dockerfile Path** | `./Dockerfile` |
| **Plan** | Free (ou selon besoins) |

### Variables d'environnement

| Key | Value | Type |
|-----|-------|------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` (ta clé Anthropic) | **Secret** |
| `DONKEY_QUOTER_API_KEY` | Cliquer "Generate" | **Secret** |
| `CLAUDE_MODEL` | `claude-3-5-haiku-20241022` | Plain |
| `CORS_ORIGINS` | `https://donkey-quoter-app.onrender.com` | Plain |

> **Important** : Note la valeur générée pour `DONKEY_QUOTER_API_KEY`, tu en auras besoin pour le service Streamlit.

### Vérification

Après déploiement, teste l'API :

- **Health check** : `https://donkey-quoter-api.onrender.com/health`
- **Documentation Swagger** : `https://donkey-quoter-api.onrender.com/docs`
- **Documentation ReDoc** : `https://donkey-quoter-api.onrender.com/redoc`

---

## Service 2 : Frontend Streamlit

### Création

1. **Dashboard Render** → **New** → **Web Service**
2. Connecter le même repository `donkey-quoter`
3. Sélectionner la même branche

### Configuration

| Paramètre | Valeur |
|-----------|--------|
| **Name** | `donkey-quoter-app` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install uv && uv sync` |
| **Start Command** | `uv run streamlit run app.py --server.port $PORT --server.address 0.0.0.0` |
| **Plan** | Free (ou selon besoins) |

### Variables d'environnement

| Key | Value | Type |
|-----|-------|------|
| `USE_API_BACKEND` | `true` | Plain |
| `API_BASE_URL` | `https://donkey-quoter-api.onrender.com` | Plain |
| `DONKEY_QUOTER_API_KEY` | (la clé générée pour l'API) | **Secret** |

### Vérification

Après déploiement, accède à l'application :

- **URL** : `https://donkey-quoter-app.onrender.com`

---

## Mise à jour du CORS

Une fois les deux services déployés, mets à jour la variable `CORS_ORIGINS` du service API avec l'URL exacte du frontend :

```
CORS_ORIGINS=https://donkey-quoter-app.onrender.com
```

---

## Dépannage

### Rate limit atteint

- Chaque clé API est limitée à 5 générations de haïkus par 24h
- Pour augmenter la limite, modifie `RateLimiter` dans `src/donkey_quoter/api/auth.py`

---

## Coûts

| Service | Plan Free | Limitations |
|---------|-----------|-------------|
| API | Gratuit | Spin down après 15min d'inactivité |
| Streamlit | Gratuit | Spin down après 15min d'inactivité |

> **Note** : Les services gratuits "spin down" après inactivité. Le premier accès peut prendre ~30 secondes.

---

## Alternative : Déploiement via Blueprint

Tu peux aussi utiliser le fichier `render.yaml` pour un déploiement automatisé :

1. **Dashboard Render** → **New** → **Blueprint**
2. Connecter le repository
3. Render détecte `render.yaml` et configure automatiquement

> **Note** : Le `render.yaml` actuel ne configure que l'API. Pour inclure Streamlit, il faudrait l'étendre.

---

## URLs de production

| Service | URL |
|---------|-----|
| API | `https://donkey-quoter-api.onrender.com` |
| Swagger | `https://donkey-quoter-api.onrender.com/docs` |
| Frontend | `https://donkey-quoter-app.onrender.com` |
