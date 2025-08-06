"""
Module pour l'intégration avec l'API Claude d'Anthropic.
"""

import os
from contextlib import contextmanager
from typing import Any, Optional

import streamlit as st
from anthropic import Anthropic, RateLimitError
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .api.exceptions import APIErrorHandler
from .config.api_pricing import CLAUDE_PRICING
from .prompts.haiku_prompts import build_haiku_prompt
from .token_counter import TokenCounter

load_dotenv()


class ClaudeAPIClient:
    """Client pour l'API Claude d'Anthropic."""

    def __init__(self):
        """Initialise le client Claude."""
        # Priorité aux secrets Streamlit, fallback vers .env
        try:
            self.api_key = st.secrets.get("ANTHROPIC_API_KEY")
        except (AttributeError, FileNotFoundError):
            self.api_key = os.getenv("ANTHROPIC_API_KEY")

        # Configuration avec fallback similaire
        try:
            self.model = st.secrets.get("CLAUDE_MODEL", "claude-3-haiku-20240307")
            self.max_tokens_input = int(st.secrets.get("MAX_TOKENS_INPUT", "200"))
            self.max_tokens_output = int(st.secrets.get("MAX_TOKENS_OUTPUT", "100"))
        except (AttributeError, FileNotFoundError):
            self.model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
            self.max_tokens_input = int(os.getenv("MAX_TOKENS_INPUT", "200"))
            self.max_tokens_output = int(os.getenv("MAX_TOKENS_OUTPUT", "100"))

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found in Streamlit secrets or environment variables"
            )

        # Ne pas créer le client ici, utiliser le context manager
        self._client = None

        # Métriques d'utilisation
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
    def _make_api_call(self, messages, model=None, max_tokens=None, temperature=0.7):
        """
        Effectue un appel API avec retry automatique pour les erreurs temporaires.

        Args:
            messages: Messages à envoyer à l'API
            model: Modèle à utiliser (par défaut self.model)
            max_tokens: Nombre max de tokens (par défaut self.max_tokens_output)
            temperature: Température pour la génération

        Returns:
            Réponse de l'API

        Raises:
            Exception: Pour les erreurs non récupérables (RateLimitError, etc.)
        """
        with self._api_call() as client:
            return client.messages.create(
                model=model or self.model,
                max_tokens=max_tokens or self.max_tokens_output,
                temperature=temperature,
                messages=messages,
            )

    def generate_haiku(
        self, quote_text: str, quote_author: str, language: str = "fr"
    ) -> Optional[str]:
        """
        Génère un haïku personnalisé basé sur une citation.

        Args:
            quote_text: Le texte de la citation
            quote_author: L'auteur de la citation
            language: La langue du haïku ('fr' ou 'en')

        Returns:
            Le haïku généré ou None en cas d'erreur
        """
        # Construire le prompt avec le module dédié
        prompt = build_haiku_prompt(quote_text, quote_author, language)

        # Limiter la longueur du prompt
        if len(prompt) > self.max_tokens_input * 4:  # Approximation
            prompt = prompt[: self.max_tokens_input * 4]

        # Appel à l'API Claude avec retry automatique
        response = self._make_api_call(messages=[{"role": "user", "content": prompt}])

        # Stocker les métriques d'utilisation
        self.last_usage_metrics = response.usage

        # Extraire le haïku de la réponse
        haiku = response.content[0].text.strip()

        # Vérifier que c'est bien un haïku (3 lignes)
        lines = haiku.split("\n")
        if len(lines) == 3:
            return haiku
        else:
            # Essayer de reformater si nécessaire
            words = haiku.split()
            if len(words) >= 10:
                # Approximation pour découper en 3 lignes
                third = len(words) // 3
                return "\n".join(
                    [
                        " ".join(words[:third]),
                        " ".join(words[third : 2 * third]),
                        " ".join(words[2 * third :]),
                    ]
                )
            return haiku

    def is_available(self) -> bool:
        """Vérifie si l'API est disponible."""
        try:
            # Test rapide de connexion avec retry
            self._make_api_call(
                messages=[{"role": "user", "content": "test"}], max_tokens=10
            )
            return True
        except Exception:
            return False

    def get_last_usage_metrics(self) -> Optional[dict[str, int]]:
        """
        Retourne les métriques d'utilisation du dernier appel API.

        Returns:
            Dict avec les clés:
            - input_tokens: Nombre de tokens d'entrée
            - output_tokens: Nombre de tokens de sortie
        """
        if not self.last_usage_metrics:
            return None

        return {
            "input_tokens": self.last_usage_metrics.input_tokens,
            "output_tokens": self.last_usage_metrics.output_tokens,
        }

    def calculate_last_request_cost(self) -> Optional[dict[str, float]]:
        """
        Calcule le coût du dernier appel API en USD.

        Returns:
            Dict avec les clés:
            - input_cost: Coût des tokens d'entrée
            - output_cost: Coût des tokens de sortie
            - total_cost: Coût total
        """
        metrics = self.get_last_usage_metrics()
        if not metrics:
            return None

        # Utiliser la configuration centralisée
        model_pricing = CLAUDE_PRICING.get(
            self.model, CLAUDE_PRICING["claude-3-haiku-20240307"]
        )

        # Calculer les coûts
        input_cost = (metrics["input_tokens"] / 1_000_000) * model_pricing["input"]
        output_cost = (metrics["output_tokens"] / 1_000_000) * model_pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        }

    def generate_haiku_with_metrics(
        self, quote_text: str, quote_author: str, language: str = "fr"
    ) -> tuple[Optional[str], Optional[dict[str, Any]]]:
        """
        Génère un haïku et retourne les métriques d'utilisation.

        Returns:
            Tuple (haiku, metrics) où metrics contient:
            - usage: métriques de tokens
            - cost: détails des coûts
        """
        haiku = self.generate_haiku(quote_text, quote_author, language)

        if haiku and self.last_usage_metrics:
            metrics = {
                "usage": self.get_last_usage_metrics(),
                "cost": self.calculate_last_request_cost(),
            }
            return haiku, metrics

        return haiku, None

    def count_tokens_safe(self, messages: list[dict]) -> tuple[Optional[int], str]:
        """
        Compte les tokens avec gestion des limites de débit.

        Args:
            messages: Messages à compter

        Returns:
            Tuple (nombre de tokens, statut) où statut peut être:
            - "success": Succès
            - "rate_limit": Limite de débit atteinte
            - "error": Erreur API
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
