"""
Point d'entrée FastAPI pour Donkey Quoter REST API.

Lancer avec: uvicorn api:app --reload --port 8000
"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
