"""
Router pour les endpoints /haikus.
"""

import os

from fastapi import APIRouter, HTTPException, Path

from ..auth import (
    OptionalAPIKey,
    RateLimitedAPIKey,
    get_rate_limiter,
)
from ..dependencies import Language, QuoteRepo, Service, Storage
from ..schemas import (
    ErrorResponse,
    HaikuExistsResponse,
    HaikuRequest,
    HaikuResponse,
    RateLimitInfo,
)

router = APIRouter(prefix="/haikus", tags=["haikus"])


@router.post(
    "/generate",
    response_model=HaikuResponse,
    summary="Générer un haïku pour une citation",
    responses={
        404: {"model": ErrorResponse},
        429: {"model": ErrorResponse, "description": "Rate limit dépassé"},
    },
)
async def generate_haiku(
    request: HaikuRequest,
    repo: QuoteRepo,
    service: Service,
    storage: Storage,
    lang: Language,
    api_key: RateLimitedAPIKey,
):
    """
    Génère un haïku pour une citation donnée.

    - Si `force_new=False`, retourne un haïku existant s'il y en a un
    - Si `force_new=True`, génère un nouveau haïku via l'API Claude (rate limited)

    Requiert une API key valide et est soumis au rate limiting (5/24h par clé).
    """
    # Trouver la citation
    quote = service.find_quote_by_id(repo.quotes, request.quote_id)
    if not quote:
        raise HTTPException(
            status_code=404, detail=f"Citation {request.quote_id} non trouvée"
        )

    # Si pas de force_new, chercher un haïku existant d'abord
    if not request.force_new:
        stored = storage.get_haiku_with_metadata(request.quote_id, lang)
        if stored:
            return HaikuResponse(
                quote_id=request.quote_id,
                haiku_text=stored["text"],
                language=lang,
                model=stored.get("model", "unknown"),
                was_generated=False,
                generated_at=stored.get("generated_at"),
            )

    # Vérifier si l'API client est disponible
    if not service.api_client:
        # Fallback vers un haïku existant ou par défaut
        stored = storage.get_haiku_with_metadata(request.quote_id, lang)
        if stored:
            return HaikuResponse(
                quote_id=request.quote_id,
                haiku_text=stored["text"],
                language=lang,
                model=stored.get("model", "unknown"),
                was_generated=False,
                generated_at=stored.get("generated_at"),
            )

        # Haïku de fallback
        fallback = service.get_fallback_haiku(lang)
        return HaikuResponse(
            quote_id=request.quote_id,
            haiku_text=fallback,
            language=lang,
            model="fallback",
            was_generated=False,
        )

    # Générer via l'API
    quote_text = quote.text.get(lang, quote.text.get("fr", ""))
    quote_author = quote.author.get(lang, quote.author.get("fr", ""))

    haiku_text = service.generate_via_api(quote_text, quote_author, lang)

    if haiku_text is None:
        # Échec de génération - fallback
        fallback = service.get_fallback_haiku(lang)
        return HaikuResponse(
            quote_id=request.quote_id,
            haiku_text=fallback,
            language=lang,
            model="fallback",
            was_generated=False,
        )

    # Enregistrer la génération pour le rate limit
    limiter = get_rate_limiter()
    limiter.record(api_key)

    # Sauvegarder le haïku
    model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
    storage.add_haiku(request.quote_id, haiku_text, lang, model)

    return HaikuResponse(
        quote_id=request.quote_id,
        haiku_text=haiku_text,
        language=lang,
        model=model,
        was_generated=True,
    )


@router.get(
    "/rate-limit",
    response_model=RateLimitInfo,
    summary="Obtenir le statut du rate limit",
)
async def get_rate_limit_status(
    api_key: OptionalAPIKey = None,
):
    """
    Retourne le statut du rate limit pour l'API key fournie.

    Sans API key, retourne les informations générales.
    """
    limiter = get_rate_limiter()

    if api_key:
        remaining = limiter.get_remaining(api_key)
    else:
        remaining = limiter.limit

    return RateLimitInfo(
        remaining=remaining,
        limit=limiter.limit,
    )


@router.get(
    "/{quote_id}",
    response_model=HaikuResponse,
    summary="Obtenir un haïku existant",
    responses={404: {"model": ErrorResponse}},
)
async def get_haiku(
    storage: Storage,
    lang: Language,
    quote_id: str = Path(..., description="ID de la citation"),
    api_key: OptionalAPIKey = None,
):
    """Retourne le haïku stocké pour une citation."""
    stored = storage.get_haiku_with_metadata(quote_id, lang)

    if not stored:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun haïku trouvé pour la citation {quote_id} en {lang}",
        )

    return HaikuResponse(
        quote_id=quote_id,
        haiku_text=stored["text"],
        language=lang,
        model=stored.get("model", "unknown"),
        was_generated=False,
        generated_at=stored.get("generated_at"),
    )


@router.get(
    "/{quote_id}/exists",
    response_model=HaikuExistsResponse,
    summary="Vérifier si un haïku existe",
)
async def haiku_exists(
    storage: Storage,
    lang: Language,
    quote_id: str = Path(..., description="ID de la citation"),
    api_key: OptionalAPIKey = None,
):
    """Vérifie si un haïku existe pour une citation."""
    exists = storage.has_haiku(quote_id, lang)
    count = storage.count_haikus(quote_id, lang) if exists else 0

    return HaikuExistsResponse(
        quote_id=quote_id,
        language=lang,
        exists=exists,
        count=count,
    )
