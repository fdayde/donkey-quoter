"""
Module pour l'intégration avec l'API Claude d'Anthropic.
"""

import os
from contextlib import contextmanager
from typing import Any, Optional

import streamlit as st
from anthropic import Anthropic, APIError, APITimeoutError, RateLimitError
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_not_exception_type,
    stop_after_attempt,
    wait_exponential,
)

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
        except RateLimitError as e:
            raise Exception(
                "Limite de crédit API atteinte. Veuillez vérifier votre compte Anthropic."
            ) from e
        except APITimeoutError as e:
            raise Exception(
                "Délai d'attente dépassé. Vérifiez votre connexion internet."
            ) from e
        except APIError as e:
            error_msg = str(e).lower()
            if "unauthorized" in error_msg or "api_key" in error_msg:
                raise Exception(
                    "Clé API invalide. Veuillez vérifier votre configuration."
                ) from e
            else:
                raise Exception(f"Erreur API : {str(e)[:100]}...") from e
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "network" in error_msg:
                raise Exception(
                    "Erreur de connexion. Vérifiez votre connexion internet."
                ) from e
            else:
                raise Exception(
                    f"Erreur lors de la génération : {str(e)[:100]}..."
                ) from e

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
        # Prompt adapté selon la langue
        if language == "fr":
            prompt = f"""Génère un haïku en français inspiré de cette citation :
"{quote_text}" - {quote_author}

Le haïku doit :
- Respecter le format 5-7-5 syllabes
- Capturer l'essence de la citation
- Utiliser une imagerie poétique avec un âne/baudet/bourrique
- Être contemplatif et philosophique

Réponds uniquement avec le haïku (3 lignes), sans explication."""
        else:
            prompt = f"""Generate an English haiku inspired by this quote:
"{quote_text}" - {quote_author}

The haiku must:
- Follow the 5-7-5 syllable format
- Capture the essence of the quote
- Use poetic imagery with a donkey/mule/ass
- Be contemplative and philosophical

Reply only with the haiku (3 lines), no explanation."""

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

        # Prix par défaut pour Claude 3 Haiku
        pricing = {
            "claude-3-haiku-20240307": {
                "input": 0.25,  # $0.25 par million de tokens
                "output": 1.25,  # $1.25 par million de tokens
            },
            "claude-3-5-haiku-20241022": {
                "input": 0.80,  # $0.80 par million de tokens
                "output": 4.00,  # $4.00 par million de tokens
            },
        }

        # Sélectionner les prix selon le modèle
        model_pricing = pricing.get(self.model, pricing["claude-3-haiku-20240307"])

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
