"""
Adaptateur pour utiliser HaikuService et DataStorage avec l'interface existante.
"""

from pathlib import Path
from typing import Optional

import streamlit as st

from ..claude_api import ClaudeAPIClient
from .haiku_service import HaikuService
from .models import Quote
from .storage import DataStorage


class HaikuAdapter:
    """Adaptateur qui utilise les services core mais maintient l'interface de HaikuGenerator."""

    def __init__(self, data_dir: Path = None):
        """Initialise l'adaptateur avec les services."""
        # Initialiser les services
        self.storage = DataStorage(data_dir)
        self.haiku_service = HaikuService()

        # Initialiser le client API
        self.api_client = None
        try:
            self.api_client = ClaudeAPIClient()
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
        return self.api_client is not None

    def can_generate_haiku(self) -> bool:
        """Vérifie si on peut générer un nouveau haïku."""
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
        # Utiliser le service pour déterminer la stratégie
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
        return self.storage.has_haiku(quote.id, language)

    def get_generation_count(self) -> int:
        """Retourne le nombre de haïkus générés dans cette session."""
        return st.session_state.haiku_generation_count

    def get_remaining_generations(self) -> int:
        """Retourne le nombre de générations restantes."""
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
        # Utiliser notre storage pour récupérer le haïku avec métadonnées
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
