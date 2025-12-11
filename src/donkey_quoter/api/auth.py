"""
Authentification par API key et rate limiting.
"""

import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

# Header pour l'API key
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyManager:
    """
    Gestionnaire des clés API.

    En production, remplacer par une base de données ou un service d'auth.
    """

    def __init__(self):
        # Clés API valides (charger depuis env ou fichier)
        self._valid_keys: set[str] = set()
        self._load_keys()

    def _load_keys(self):
        """Charge les clés API depuis l'environnement."""
        # Clé principale depuis .env
        main_key = os.getenv("DONKEY_QUOTER_API_KEY")
        if main_key:
            self._valid_keys.add(main_key)

        # Clés supplémentaires (comma-separated)
        extra_keys = os.getenv("DONKEY_QUOTER_API_KEYS", "")
        if extra_keys:
            for key in extra_keys.split(","):
                key = key.strip()
                if key:
                    self._valid_keys.add(key)

        # Clé de développement (uniquement si explicitement activée)
        if os.getenv("DONKEY_QUOTER_DEV_MODE", "").lower() == "true":
            self._valid_keys.add("dev-key-for-testing")

    def is_valid(self, api_key: str) -> bool:
        """Vérifie si une clé API est valide."""
        return api_key in self._valid_keys

    def add_key(self, api_key: str):
        """Ajoute une clé API (pour les tests)."""
        self._valid_keys.add(api_key)


class RateLimiter:
    """
    Rate limiter par API key.

    Limite le nombre de générations de haïkus par clé API.
    """

    def __init__(self, limit: int = 5, window_hours: int = 24):
        self.limit = limit
        self.window = timedelta(hours=window_hours)
        # {api_key: [datetime, datetime, ...]}
        self._usage: dict[str, list[datetime]] = defaultdict(list)

    def _cleanup(self, api_key: str):
        """Nettoie les entrées expirées."""
        cutoff = datetime.utcnow() - self.window
        self._usage[api_key] = [ts for ts in self._usage[api_key] if ts > cutoff]

    def check(self, api_key: str) -> tuple[bool, int]:
        """
        Vérifie si l'API key peut faire une génération.

        Returns:
            (is_allowed, remaining_count)
        """
        self._cleanup(api_key)
        count = len(self._usage[api_key])
        remaining = max(0, self.limit - count)
        return count < self.limit, remaining

    def record(self, api_key: str):
        """Enregistre une génération."""
        self._usage[api_key].append(datetime.utcnow())

    def get_remaining(self, api_key: str) -> int:
        """Retourne le nombre de générations restantes."""
        self._cleanup(api_key)
        return max(0, self.limit - len(self._usage[api_key]))

    def reset(self, api_key: str):
        """Reset le compteur pour une clé (pour les tests)."""
        self._usage[api_key] = []


# Instances globales (singleton-like)
_api_key_manager: Optional[APIKeyManager] = None
_rate_limiter: Optional[RateLimiter] = None


def get_api_key_manager() -> APIKeyManager:
    """Retourne le gestionnaire d'API keys (singleton)."""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


def get_rate_limiter() -> RateLimiter:
    """Retourne le rate limiter (singleton)."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


async def verify_api_key(
    api_key: str = Security(API_KEY_HEADER),
) -> str:
    """
    Dépendance FastAPI pour vérifier l'API key.

    Usage:
        @router.post("/endpoint")
        async def endpoint(api_key: str = Depends(verify_api_key)):
            ...
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    manager = get_api_key_manager()
    if not manager.is_valid(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


async def verify_api_key_optional(
    api_key: str = Security(API_KEY_HEADER),
) -> Optional[str]:
    """
    Dépendance pour vérifier l'API key de manière optionnelle.

    Retourne None si pas de clé, la clé si valide, ou lève une erreur si invalide.
    """
    if not api_key:
        return None

    manager = get_api_key_manager()
    if not manager.is_valid(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


async def check_haiku_rate_limit(
    api_key: str = Depends(verify_api_key),
) -> str:
    """
    Vérifie le rate limit pour la génération de haïkus.

    Lève une exception 429 si la limite est atteinte.
    """
    limiter = get_rate_limiter()
    allowed, remaining = limiter.check(api_key)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={
                "X-RateLimit-Limit": str(limiter.limit),
                "X-RateLimit-Remaining": "0",
                "Retry-After": "3600",
            },
        )

    return api_key


# Type aliases pour les signatures de routes
VerifiedAPIKey = Annotated[str, Depends(verify_api_key)]
OptionalAPIKey = Annotated[Optional[str], Depends(verify_api_key_optional)]
RateLimitedAPIKey = Annotated[str, Depends(check_haiku_rate_limit)]
