"""
Client API Anthropic pour l'infrastructure (séparé de la logique métier).
"""

import os
from contextlib import contextmanager
from typing import Optional

import streamlit as st
from anthropic import Anthropic, RateLimitError
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..api.exceptions import APIErrorHandler
from ..token_counter import TokenCounter

load_dotenv()


class AnthropicClient:
    """Client API pur pour Anthropic Claude (infrastructure uniquement)."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialise le client Anthropic.

        Args:
            api_key: Clé API Anthropic (optionnel, utilise les secrets/env par défaut)
            model: Modèle à utiliser (optionnel, utilise les secrets/env par défaut)
        """
        # Priorité aux secrets Streamlit, fallback vers .env
        if api_key:
            self.api_key = api_key
        else:
            try:
                self.api_key = st.secrets.get("ANTHROPIC_API_KEY")
            except (AttributeError, FileNotFoundError):
                self.api_key = os.getenv("ANTHROPIC_API_KEY")

        # Configuration du modèle
        if model:
            self.model = model
        else:
            try:
                self.model = st.secrets.get("CLAUDE_MODEL", "claude-3-haiku-20240307")
            except (AttributeError, FileNotFoundError):
                self.model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")

        # Configuration des tokens
        try:
            self.max_tokens_input = int(st.secrets.get("MAX_TOKENS_INPUT", "200"))
            self.max_tokens_output = int(st.secrets.get("MAX_TOKENS_OUTPUT", "100"))
        except (AttributeError, FileNotFoundError):
            self.max_tokens_input = int(os.getenv("MAX_TOKENS_INPUT", "200"))
            self.max_tokens_output = int(os.getenv("MAX_TOKENS_OUTPUT", "100"))

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in Streamlit secrets or environment variables"
            )

        # Client lazy loading
        self._client = None

        # Métriques d'utilisation pour le dernier appel
        self.last_usage_metrics = None

        # Compteur pour count_tokens
        self.token_counter = TokenCounter()

    @property
    def client(self) -> Anthropic:
        """Retourne le client Anthropic (lazy loading)."""
        if self._client is None:
            self._client = Anthropic(api_key=self.api_key)
        return self._client

    @contextmanager
    def _api_call(self):
        """Context manager pour les appels API avec gestion d'erreur."""
        try:
            yield self.client
        except Exception as e:
            raise APIErrorHandler.handle_api_error(e) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_not_exception_type(RateLimitError),
        reraise=True,
    )
    def call_claude(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ) -> str:
        """
        Effectue un appel générique à l'API Claude.

        Args:
            prompt: Le prompt à envoyer
            max_tokens: Nombre max de tokens de sortie
            temperature: Température pour la génération
            model: Modèle à utiliser (optionnel)

        Returns:
            La réponse brute de l'API

        Raises:
            Exception: Pour les erreurs non récupérables
        """
        messages = [{"role": "user", "content": prompt}]

        with self._api_call() as client:
            response = client.messages.create(
                model=model or self.model,
                max_tokens=max_tokens or self.max_tokens_output,
                temperature=temperature,
                messages=messages,
            )

        # Stocker les métriques d'utilisation
        self.last_usage_metrics = response.usage

        # Retourner le texte brut
        return response.content[0].text.strip()

    def is_available(self) -> bool:
        """Vérifie si l'API est disponible."""
        try:
            # Test rapide de connexion
            self.call_claude("test", max_tokens=10)
            return True
        except Exception:
            return False

    def get_last_usage_metrics(self) -> Optional[dict[str, int]]:
        """
        Retourne les métriques d'utilisation du dernier appel API.

        Returns:
            Dict avec input_tokens et output_tokens ou None
        """
        if not self.last_usage_metrics:
            return None

        return {
            "input_tokens": self.last_usage_metrics.input_tokens,
            "output_tokens": self.last_usage_metrics.output_tokens,
        }

    def count_tokens_safe(self, messages: list[dict]) -> tuple[Optional[int], str]:
        """
        Compte les tokens avec gestion des limites de débit.

        Args:
            messages: Messages à compter

        Returns:
            Tuple (nombre de tokens, statut)
        """
        if not self.token_counter.can_count_tokens():
            return None, "rate_limit"

        try:
            with self._api_call() as client:
                response = client.messages.count_tokens(
                    messages=messages, model=self.model
                )
                self.token_counter.increment()
                return response.input_tokens, "success"
        except Exception:
            return None, "error"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_not_exception_type(RateLimitError),
        reraise=True,
    )
    def _make_api_call(self, messages, model=None, max_tokens=None, temperature=0.7):
        """
        Effectue un appel API bas niveau avec retry automatique.
        DEPRECATED: Utiliser call_claude() à la place.
        """
        with self._api_call() as client:
            return client.messages.create(
                model=model or self.model,
                max_tokens=max_tokens or self.max_tokens_output,
                temperature=temperature,
                messages=messages,
            )
