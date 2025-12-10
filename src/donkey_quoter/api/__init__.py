"""
Module API REST Donkey Quoter.

Fournit une API FastAPI pour accéder aux citations et haïkus.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import export_router, haikus_router, quotes_router
from .schemas import HealthResponse


def _get_cors_origins() -> list[str]:
    """
    Récupère les origines CORS autorisées depuis l'environnement.

    En dev: ["*"] (tout autorisé)
    En prod: liste d'origines spécifiques depuis CORS_ORIGINS
    """
    origins = os.getenv("CORS_ORIGINS", "")
    if origins:
        return [o.strip() for o in origins.split(",") if o.strip()]
    # Fallback dev mode
    return ["*"]


def create_app() -> FastAPI:
    """
    Factory pour créer l'application FastAPI.

    Returns:
        Instance FastAPI configurée
    """
    app = FastAPI(
        title="Donkey Quoter API",
        description="API REST pour découvrir des citations et générer des haïkus",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS middleware (configurable via CORS_ORIGINS env var)
    cors_origins = _get_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclure les routers
    app.include_router(quotes_router)
    app.include_router(haikus_router)
    app.include_router(export_router)

    @app.get("/", response_model=HealthResponse, tags=["health"])
    async def root():
        """Health check - endpoint racine."""
        return HealthResponse()

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health():
        """Health check détaillé."""
        return HealthResponse(status="healthy")

    return app


# Instance de l'application pour uvicorn
app = create_app()
