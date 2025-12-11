"""
Injection de dépendances pour l'API FastAPI.
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Optional

from dotenv import load_dotenv
from fastapi import Depends, Header, Query

from ..core.data_loader import DataLoader
from ..core.models import Quote
from ..core.services import DonkeyQuoterService
from ..core.storage import DataStorage
from ..infrastructure.anthropic_client import AnthropicClient


class QuoteRepository:
    """
    Repository pour les citations.

    Gère le chargement et le cache des citations.
    """

    def __init__(self):
        self.data_loader = DataLoader()
        self._quotes: Optional[list[Quote]] = None

    @property
    def quotes(self) -> list[Quote]:
        """Retourne la liste des citations (lazy loading)."""
        if self._quotes is None:
            self._quotes = self.data_loader.load_quotes(
                self.data_loader.get_default_quotes_path()
            )
        return self._quotes

    def reload(self):
        """Force le rechargement des citations depuis le disque."""
        self._quotes = None

    def get_by_id(self, quote_id: str) -> Optional[Quote]:
        """Trouve une citation par son ID."""
        for quote in self.quotes:
            if quote.id == quote_id:
                return quote
        return None


@lru_cache
def get_quote_repository() -> QuoteRepository:
    """Singleton pour le repository de citations."""
    return QuoteRepository()


@lru_cache
def get_storage() -> DataStorage:
    """Singleton pour le storage des haïkus."""
    return DataStorage(Path("data"))


_anthropic_client: Optional[AnthropicClient] = None


def get_anthropic_client() -> Optional[AnthropicClient]:
    """
    Retourne le client Anthropic s'il est configuré.

    Retourne None si la clé API n'est pas disponible.
    """
    global _anthropic_client
    if _anthropic_client is None:
        # Charger les variables d'environnement avant de créer le client
        load_dotenv()
        try:
            _anthropic_client = AnthropicClient(config_source="env")
            print(
                f"[API] AnthropicClient initialized with model: {_anthropic_client.model}"
            )
        except ValueError as e:
            print(f"[API] AnthropicClient initialization failed: {e}")
            return None
    return _anthropic_client


def get_service(
    storage: Annotated[DataStorage, Depends(get_storage)],
    api_client: Annotated[Optional[AnthropicClient], Depends(get_anthropic_client)],
) -> DonkeyQuoterService:
    """Retourne le service métier avec le client API."""
    return DonkeyQuoterService(storage=storage, api_client=api_client)


def get_language(
    accept_language: Annotated[Optional[str], Header(alias="Accept-Language")] = None,
    lang: Annotated[Optional[str], Query(description="Code langue (fr/en)")] = None,
) -> str:
    """
    Détermine la langue depuis le header ou query param.

    Priorité: query param > header > défaut (fr)
    """
    if lang and lang in ("fr", "en"):
        return lang

    if accept_language:
        accept_lower = accept_language.lower()
        if "en" in accept_lower:
            return "en"
        if "fr" in accept_lower:
            return "fr"

    return "fr"


# Type aliases pour les signatures de routes
QuoteRepo = Annotated[QuoteRepository, Depends(get_quote_repository)]
Storage = Annotated[DataStorage, Depends(get_storage)]
Service = Annotated[DonkeyQuoterService, Depends(get_service)]
Language = Annotated[str, Depends(get_language)]
APIClient = Annotated[Optional[AnthropicClient], Depends(get_anthropic_client)]
