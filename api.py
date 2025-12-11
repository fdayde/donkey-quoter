"""
Point d'entrée FastAPI pour Donkey Quoter REST API.

Lancer avec: uvicorn api:app --reload --port 8001
"""

from src.donkey_quoter.api import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
