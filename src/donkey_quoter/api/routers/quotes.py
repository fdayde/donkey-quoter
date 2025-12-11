"""
Router pour les endpoints /quotes.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query

from ..auth import OptionalAPIKey
from ..dependencies import Language, QuoteRepo, Service
from ..schemas import (
    ErrorResponse,
    QuoteInputModel,
    QuoteListResponse,
    QuoteResponse,
)

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get(
    "/random",
    response_model=QuoteResponse,
    summary="Obtenir une citation aléatoire",
    responses={404: {"model": ErrorResponse}},
)
async def get_random_quote(
    repo: QuoteRepo,
    service: Service,
    lang: Language,
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    api_key: OptionalAPIKey = None,
):
    """Retourne une citation aléatoire, optionnellement filtrée par catégorie."""
    quotes = repo.quotes

    if category and category != "all":
        quotes = service.filter_by_category(quotes, category)

    if not quotes:
        raise HTTPException(status_code=404, detail="Aucune citation trouvée")

    quote = service.get_random_quote(quotes)
    return QuoteResponse(data=quote, language=lang)


@router.get(
    "",
    response_model=QuoteListResponse,
    summary="Lister les citations",
)
async def list_quotes(
    repo: QuoteRepo,
    service: Service,
    lang: Language,
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    quote_type: Optional[str] = Query(
        None, alias="type", description="Filtrer par type"
    ),
    limit: int = Query(50, ge=1, le=100, description="Nombre max de résultats"),
    offset: int = Query(0, ge=0, description="Offset pour pagination"),
    api_key: OptionalAPIKey = None,
):
    """Liste les citations avec filtres optionnels et pagination."""
    quotes = repo.quotes

    if category and category != "all":
        quotes = service.filter_by_category(quotes, category)

    if quote_type and quote_type != "all":
        quotes = service.filter_by_type(quotes, quote_type)

    total = len(quotes)
    quotes = quotes[offset : offset + limit]

    return QuoteListResponse(data=quotes, total=total, language=lang)


@router.get(
    "/{quote_id}",
    response_model=QuoteResponse,
    summary="Obtenir une citation par ID",
    responses={404: {"model": ErrorResponse}},
)
async def get_quote(
    repo: QuoteRepo,
    service: Service,
    lang: Language,
    quote_id: str = Path(..., description="ID de la citation"),
    api_key: OptionalAPIKey = None,
):
    """Retourne une citation par son ID."""
    quote = service.find_quote_by_id(repo.quotes, quote_id)

    if not quote:
        raise HTTPException(status_code=404, detail=f"Citation {quote_id} non trouvée")

    return QuoteResponse(data=quote, language=lang)


@router.post(
    "",
    response_model=QuoteResponse,
    status_code=201,
    summary="Créer une nouvelle citation",
)
async def create_quote(
    quote_input: QuoteInputModel,
    service: Service,
    lang: Language,
    api_key: OptionalAPIKey = None,
):
    """
    Crée une nouvelle citation utilisateur.

    Note: La citation est créée en mémoire et n'est pas persistée.
    """
    quote = service.create_quote_from_input(quote_input, lang)
    return QuoteResponse(data=quote, language=lang)
