"""
Schémas de requête/réponse pour l'API REST.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..core.models import Quote, QuoteInput

# Re-export des modèles existants
QuoteModel = Quote
QuoteInputModel = QuoteInput


class QuoteResponse(BaseModel):
    """Réponse API pour une citation."""

    data: Quote
    language: str = "fr"


class QuoteListResponse(BaseModel):
    """Réponse API pour une liste de citations."""

    data: list[Quote]
    total: int
    language: str = "fr"


class HaikuRequest(BaseModel):
    """Requête pour générer un haïku."""

    quote_id: str = Field(..., description="ID de la citation source")
    force_new: bool = Field(
        default=False, description="Forcer la génération d'un nouveau haïku"
    )


class HaikuResponse(BaseModel):
    """Réponse API pour un haïku."""

    quote_id: str
    haiku_text: str
    language: str
    model: str = "unknown"
    was_generated: bool = False
    generated_at: Optional[datetime] = None


class HaikuExistsResponse(BaseModel):
    """Réponse pour la vérification d'existence d'un haïku."""

    quote_id: str
    language: str
    exists: bool
    count: int = 0


class RateLimitInfo(BaseModel):
    """Information sur le rate limit."""

    remaining: int
    limit: int = 5
    reset_info: str = "24h window per API key"


class ExportResponse(BaseModel):
    """Réponse pour l'export des données."""

    quotes: list[Quote]
    haikus: dict
    export_date: datetime
    total_quotes: int


class ErrorResponse(BaseModel):
    """Réponse d'erreur standard."""

    error: str
    detail: Optional[str] = None
    code: str


class HealthResponse(BaseModel):
    """Réponse du health check."""

    status: str = "ok"
    service: str = "donkey-quoter-api"
    version: str = "1.0.0"
