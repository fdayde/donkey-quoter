"""
Client HTTP pour appeler l'API REST Donkey Quoter.

Utilisé par Streamlit pour communiquer avec le backend API.
"""

import os
from typing import Optional

import httpx

from ..core.models import Quote


class DonkeyQuoterAPIClient:
    """
    Client HTTP pour l'API Donkey Quoter.

    Permet à Streamlit d'appeler l'API REST au lieu d'utiliser
    directement les services.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialise le client API.

        Args:
            base_url: URL de base de l'API (défaut: depuis env ou localhost:8000)
            api_key: Clé API pour l'authentification
            timeout: Timeout pour les requêtes HTTP
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("DONKEY_QUOTER_API_KEY")
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Retourne le client HTTP (lazy loading)."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
            )
        return self._client

    def close(self):
        """Ferme le client HTTP."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ================================================================
    # Quotes API
    # ================================================================

    def get_quotes(
        self,
        language: str = "fr",
        category: Optional[str] = None,
        quote_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Quote]:
        """
        Récupère la liste des citations.

        Args:
            language: Langue (fr/en)
            category: Filtrer par catégorie
            quote_type: Filtrer par type
            limit: Nombre max de résultats
            offset: Offset pour pagination

        Returns:
            Liste de citations
        """
        params = {"lang": language, "limit": limit, "offset": offset}
        if category:
            params["category"] = category
        if quote_type:
            params["type"] = quote_type

        response = self.client.get("/quotes", params=params)
        response.raise_for_status()

        data = response.json()
        return [Quote(**q) for q in data["data"]]

    def get_random_quote(
        self,
        language: str = "fr",
        category: Optional[str] = None,
    ) -> Optional[Quote]:
        """
        Récupère une citation aléatoire.

        Args:
            language: Langue (fr/en)
            category: Filtrer par catégorie

        Returns:
            Citation aléatoire ou None
        """
        params = {"lang": language}
        if category:
            params["category"] = category

        try:
            response = self.client.get("/quotes/random", params=params)
            response.raise_for_status()
            data = response.json()
            return Quote(**data["data"])
        except httpx.HTTPStatusError:
            return None

    def get_quote_by_id(
        self,
        quote_id: str,
        language: str = "fr",
    ) -> Optional[Quote]:
        """
        Récupère une citation par son ID.

        Args:
            quote_id: ID de la citation
            language: Langue (fr/en)

        Returns:
            Citation ou None
        """
        try:
            response = self.client.get(f"/quotes/{quote_id}", params={"lang": language})
            response.raise_for_status()
            data = response.json()
            return Quote(**data["data"])
        except httpx.HTTPStatusError:
            return None

    def create_quote(
        self,
        text: str,
        author: str,
        category: str = "personal",
        language: str = "fr",
    ) -> Optional[Quote]:
        """
        Crée une nouvelle citation.

        Args:
            text: Texte de la citation
            author: Auteur
            category: Catégorie
            language: Langue

        Returns:
            Citation créée ou None
        """
        try:
            response = self.client.post(
                "/quotes",
                json={"text": text, "author": author, "category": category},
                params={"lang": language},
            )
            response.raise_for_status()
            data = response.json()
            return Quote(**data["data"])
        except httpx.HTTPStatusError:
            return None

    # ================================================================
    # Haikus API
    # ================================================================

    def get_haiku(
        self,
        quote_id: str,
        language: str = "fr",
    ) -> Optional[dict]:
        """
        Récupère un haïku existant.

        Args:
            quote_id: ID de la citation
            language: Langue (fr/en)

        Returns:
            Dict avec haiku_text, model, was_generated ou None
        """
        try:
            response = self.client.get(f"/haikus/{quote_id}", params={"lang": language})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return None

    def generate_haiku(
        self,
        quote_id: str,
        language: str = "fr",
        force_new: bool = False,
    ) -> Optional[dict]:
        """
        Génère un haïku pour une citation.

        Args:
            quote_id: ID de la citation
            language: Langue (fr/en)
            force_new: Forcer une nouvelle génération

        Returns:
            Dict avec haiku_text, model, was_generated ou None
        """
        try:
            response = self.client.post(
                "/haikus/generate",
                json={"quote_id": quote_id, "force_new": force_new},
                params={"lang": language},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Gérer le rate limit
            if e.response.status_code == 429:
                return {"error": "rate_limit", "detail": "Rate limit exceeded"}
            return None

    def haiku_exists(
        self,
        quote_id: str,
        language: str = "fr",
    ) -> bool:
        """
        Vérifie si un haïku existe.

        Args:
            quote_id: ID de la citation
            language: Langue (fr/en)

        Returns:
            True si un haïku existe
        """
        try:
            response = self.client.get(
                f"/haikus/{quote_id}/exists", params={"lang": language}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("exists", False)
        except httpx.HTTPStatusError:
            return False

    def get_rate_limit_status(self) -> dict:
        """
        Récupère le statut du rate limit.

        Returns:
            Dict avec remaining et limit
        """
        try:
            response = self.client.get("/haikus/rate-limit")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return {"remaining": 0, "limit": 5}

    # ================================================================
    # Export API
    # ================================================================

    def export_data(self) -> Optional[dict]:
        """
        Exporte toutes les données.

        Returns:
            Dict avec quotes, haikus, export_date ou None
        """
        try:
            response = self.client.get("/export")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError:
            return None

    # ================================================================
    # Health API
    # ================================================================

    def is_available(self) -> bool:
        """
        Vérifie si l'API est disponible.

        Returns:
            True si l'API répond
        """
        try:
            response = self.client.get("/health")
            return response.status_code == 200
        except Exception:
            return False


# Singleton pour usage global
_api_client: Optional[DonkeyQuoterAPIClient] = None


def get_api_client() -> DonkeyQuoterAPIClient:
    """Retourne le client API singleton."""
    global _api_client
    if _api_client is None:
        _api_client = DonkeyQuoterAPIClient()
    return _api_client
