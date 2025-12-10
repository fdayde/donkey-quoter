"""
Adaptateur pour utiliser HaikuService et DataStorage avec l'interface existante.

Supporte deux modes:
- Mode direct: appelle DonkeyQuoterService et AnthropicClient directement
- Mode API: appelle l'API REST via HTTP (USE_API_BACKEND=true)
"""

import os
from pathlib import Path
from typing import Optional

import streamlit as st

from ..infrastructure.anthropic_client import AnthropicClient
from .models import Quote
from .services import DonkeyQuoterService
from .storage import DataStorage

# Détermine si on utilise le backend API ou les services directs
USE_API_BACKEND = os.getenv("USE_API_BACKEND", "false").lower() == "true"


class HaikuAdapter:
    """Adaptateur qui utilise DonkeyQuoterService et DataStorage avec l'interface existante."""

    def __init__(self, data_dir: Path = None):
        """Initialise l'adaptateur avec les services ou le client API."""
        self._http_client = None

        if USE_API_BACKEND:
            # Mode API: utiliser le client HTTP
            from ..api.client import get_api_client

            self._http_client = get_api_client()
            self.storage = None
            self.haiku_service = None
            self.api_client = None  # Pas besoin du client Anthropic direct
        else:
            # Mode direct: utiliser les services locaux
            self.storage = DataStorage(data_dir)
            self.haiku_service = DonkeyQuoterService()

            # Initialiser le client API Anthropic
            self.api_client = None
            try:
                self.api_client = AnthropicClient()
                self.haiku_service.api_client = self.api_client
                self.haiku_service.storage = self.storage
            except Exception as e:
                print(f"Client API non disponible : {e}")

        # Initialiser le compteur de session pour les haïkus
        if "haiku_generation_count" not in st.session_state:
            st.session_state.haiku_generation_count = 0

    @property
    def has_api_key(self) -> bool:
        """Vérifie si une clé API est disponible."""
        if USE_API_BACKEND:
            # En mode API, on a toujours une "clé" (c'est l'API qui gère)
            return self._http_client is not None
        return self.api_client is not None

    def can_generate_haiku(self) -> bool:
        """Vérifie si on peut générer un nouveau haïku."""
        if USE_API_BACKEND and self._http_client:
            # En mode API, vérifier le rate limit distant
            status = self._http_client.get_rate_limit_status()
            return status.get("remaining", 0) > 0
        return self.haiku_service.can_generate_new_haiku(
            st.session_state.haiku_generation_count
        )

    def generate_haiku_for_quote(
        self, quote: Quote, language: str, force_new: bool = False
    ) -> tuple[Quote, bool]:
        """
        Génère un haïku pour une citation donnée.

        Args:
            quote: Citation source
            language: Langue du haïku
            force_new: Forcer une nouvelle génération

        Returns:
            Tuple (quote_haiku, was_generated_via_api)
        """
        if USE_API_BACKEND and self._http_client:
            # Mode API: appeler l'endpoint /haikus/generate
            result = self._http_client.generate_haiku(
                quote_id=quote.id,
                language=language,
                force_new=force_new,
            )

            if result is None:
                return None, False

            if result.get("error") == "rate_limit":
                return None, False

            haiku_text = result.get("haiku_text", "")
            model_used = result.get("model", "unknown")
            was_generated = result.get("was_generated", False)

            # Créer l'objet Quote pour le haïku
            from datetime import datetime

            quote_id = f"poem_{quote.id}_{int(datetime.now().timestamp())}"
            poem_quote = Quote(
                id=quote_id,
                text={
                    language: haiku_text,
                    "fr" if language == "en" else "en": haiku_text,
                },
                author={"fr": "Claude", "en": "Claude"},
                category="poem",
                type="generated",
            )

            return poem_quote, was_generated

        # Mode direct: utiliser le service local
        haiku_text, model_used, was_generated_via_api = (
            self.haiku_service.generate_haiku_strategy(
                quote, language, force_new, st.session_state.haiku_generation_count
            )
        )

        # Si pas de haïku généré et force_new, retourner None
        if haiku_text is None and force_new:
            return None, False

        # Si pas de haiku généré, utiliser fallback
        if haiku_text is None:
            haiku_text = self.haiku_service.get_fallback_haiku(language)
            model_used = "unknown"
            was_generated_via_api = False

        # Incrementer le compteur si généré via API
        if was_generated_via_api:
            st.session_state.haiku_generation_count += 1
            # Sauvegarder le haïku
            self.storage.add_haiku(quote.id, haiku_text, language, model_used)

        # Créer l'objet Quote pour le haïku
        poem_quote = self.haiku_service.create_haiku_quote(
            haiku_text, language, model_used, quote.id
        )

        return poem_quote, was_generated_via_api

    def get_stored_haiku_for_quote(
        self, quote: Quote, language: str
    ) -> Optional[Quote]:
        """
        Récupère un haïku stocké pour une citation.

        Args:
            quote: Citation source
            language: Langue du haïku

        Returns:
            Quote représentant le haïku ou None
        """
        if USE_API_BACKEND and self._http_client:
            # Mode API
            result = self._http_client.get_haiku(quote.id, language)
            if result:
                haiku_text = result.get("haiku_text", "")
                from datetime import datetime

                quote_id = f"poem_{quote.id}_{int(datetime.now().timestamp())}"
                return Quote(
                    id=quote_id,
                    text={
                        language: haiku_text,
                        "fr" if language == "en" else "en": haiku_text,
                    },
                    author={"fr": "Claude", "en": "Claude"},
                    category="poem",
                    type="generated",
                )
            return None

        # Mode direct
        haiku_text = self.storage.get_haiku(quote.id, language)
        if haiku_text:
            poem_quote = self.haiku_service.create_haiku_quote(
                haiku_text, language, "unknown", quote.id
            )
            return poem_quote
        return None

    def has_stored_haiku(self, quote: Quote, language: str) -> bool:
        """
        Vérifie si un haïku stocké existe pour une citation.

        Args:
            quote: Citation source
            language: Langue du haïku

        Returns:
            True si un haïku stocké existe
        """
        if USE_API_BACKEND and self._http_client:
            return self._http_client.haiku_exists(quote.id, language)
        return self.storage.has_haiku(quote.id, language)

    def get_generation_count(self) -> int:
        """Retourne le nombre de haïkus générés dans cette session."""
        if USE_API_BACKEND and self._http_client:
            status = self._http_client.get_rate_limit_status()
            return status.get("limit", 5) - status.get("remaining", 5)
        return st.session_state.haiku_generation_count

    def get_remaining_generations(self) -> int:
        """Retourne le nombre de générations restantes."""
        if USE_API_BACKEND and self._http_client:
            status = self._http_client.get_rate_limit_status()
            return status.get("remaining", 0)
        return max(0, 5 - st.session_state.haiku_generation_count)

    def reset_generation_count(self):
        """Remet à zéro le compteur de génération."""
        st.session_state.haiku_generation_count = 0

    def get_usage_display(self, language: str = "fr") -> str:
        """Retourne l'affichage du compteur d'usage."""
        count = st.session_state.haiku_generation_count
        remaining = max(0, 5 - count)

        if language == "fr":
            return f"Haïkus restants : {remaining}/5"
        else:
            return f"Haikus remaining: {remaining}/5"

    def get_existing_haiku(self, quote: Quote, language: str) -> Optional[Quote]:
        """
        Récupère un haïku existant pour une citation (alias pour compatibilité).

        Args:
            quote: La citation source
            language: La langue du haïku

        Returns:
            Un objet Quote contenant le haïku ou None si aucun n'existe
        """
        if USE_API_BACKEND and self._http_client:
            # Mode API
            return self.get_stored_haiku_for_quote(quote, language)

        # Mode direct - utiliser notre storage pour récupérer le haïku avec métadonnées
        haiku_data = self.storage.get_haiku_with_metadata(quote.id, language)

        if not haiku_data:
            return None

        # Utiliser le service pour créer l'objet Quote
        haiku_text = haiku_data.get("text", "")
        model = haiku_data.get("model", "unknown")

        return self.haiku_service.create_haiku_quote(
            haiku_text, language, model, quote.id
        )

    def generate_from_quote(
        self, quote: Quote, language: str, force_new: bool = False
    ) -> Optional[Quote]:
        """
        Génère un haïku basé sur une citation (alias pour compatibilité).

        Args:
            quote: La citation source
            language: La langue du haïku
            force_new: Si True, essaie toujours de générer un nouveau haïku via API

        Returns:
            Un objet Quote contenant le haïku ou None en cas d'erreur
        """
        # Vérifier les limites avant de commencer
        generation_count = st.session_state.haiku_generation_count
        if force_new and generation_count >= 5:
            return None

        try:
            # Utiliser notre méthode existante
            poem, was_generated_via_api = self.generate_haiku_for_quote(
                quote, language, force_new
            )
            return poem

        except Exception as e:
            st.error(f"⚠️ {str(e)}")
            return None
