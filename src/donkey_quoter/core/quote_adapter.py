"""
Adaptateur pour utiliser QuoteService avec l'interface de QuoteManager existante.

Supporte deux modes:
- Mode direct: appelle DonkeyQuoterService directement (USE_API_BACKEND=false)
- Mode API: appelle l'API REST via HTTP (USE_API_BACKEND=true)
"""

import os
from typing import Optional

import streamlit as st

from .models import Quote, QuoteInput
from .services import DonkeyQuoterService

# Détermine si on utilise le backend API ou les services directs
USE_API_BACKEND = os.getenv("USE_API_BACKEND", "false").lower() == "true"


class QuoteAdapter:
    """Adaptateur qui utilise DonkeyQuoterService mais maintient l'interface de QuoteManager."""

    def __init__(self):
        """Initialise l'adaptateur avec le service ou le client API."""
        self._api_client = None

        if USE_API_BACKEND:
            # Mode API: utiliser le client HTTP
            from ..api.client import get_api_client

            self._api_client = get_api_client()
            self.service = None
        else:
            # Mode direct: utiliser le service
            self.service = DonkeyQuoterService()

        # Initialiser le state si nécessaire (comme le faisait QuoteManager)
        if "quotes" not in st.session_state:
            if USE_API_BACKEND and self._api_client:
                # Charger les quotes depuis l'API
                try:
                    st.session_state.quotes = self._api_client.get_quotes(limit=100)
                except Exception:
                    # Fallback vers le chargement local
                    from ..core.data_loader import DataLoader

                    data_loader = DataLoader()
                    st.session_state.quotes = data_loader.load_quotes(
                        data_loader.get_default_quotes_path()
                    )
            else:
                from ..core.data_loader import DataLoader

                data_loader = DataLoader()
                st.session_state.quotes = data_loader.load_quotes(
                    data_loader.get_default_quotes_path()
                )
        if "saved_quotes" not in st.session_state:
            st.session_state.saved_quotes = []
        if "saved_poems" not in st.session_state:
            st.session_state.saved_poems = []
        if "original_quote" not in st.session_state:
            st.session_state.original_quote = None

    @property
    def quotes(self) -> list[Quote]:
        """Retourne la liste des citations."""
        return st.session_state.quotes

    @property
    def current_quote(self) -> Optional[Quote]:
        """Retourne la citation courante."""
        return st.session_state.current_quote

    @current_quote.setter
    def current_quote(self, quote: Quote):
        """Définit la citation courante."""
        st.session_state.current_quote = quote

    @property
    def saved_quotes(self) -> list[Quote]:
        """Retourne les citations sauvegardées."""
        return st.session_state.saved_quotes

    @property
    def saved_poems(self) -> list[Quote]:
        """Retourne les poèmes sauvegardés."""
        return st.session_state.saved_poems

    @property
    def original_quote(self) -> Optional[Quote]:
        """Retourne la citation originale (avant génération de haïku)."""
        return st.session_state.original_quote

    @original_quote.setter
    def original_quote(self, quote: Optional[Quote]):
        """Définit la citation originale."""
        st.session_state.original_quote = quote

    def get_text(self, text_dict: dict[str, str], language: str) -> str:
        """Obtient le texte dans la langue spécifiée."""
        # Cette méthode est purement locale, pas besoin d'appeler l'API
        if isinstance(text_dict, dict):
            return text_dict.get(language, text_dict.get("fr", ""))
        return str(text_dict)

    def add_quote(self, quote_input: QuoteInput, language: str) -> Quote:
        """Ajoute une nouvelle citation."""
        if USE_API_BACKEND and self._api_client:
            # Mode API
            quote = self._api_client.create_quote(
                text=quote_input.text,
                author=quote_input.author,
                category=quote_input.category,
                language=language,
            )
            if quote:
                # Ajouter localement aussi pour la session
                st.session_state.quotes.insert(0, quote)
                self.current_quote = quote
                if quote not in st.session_state.saved_quotes:
                    st.session_state.saved_quotes.append(quote)
            return quote
        else:
            # Mode direct
            quote = self.service.create_quote_from_input(quote_input, language)
            st.session_state.quotes = self.service.add_quote_to_list(
                st.session_state.quotes, quote
            )
            self.current_quote = quote
            # Sauvegarder automatiquement
            st.session_state.saved_quotes, _ = self.service.add_quote_if_not_exists(
                st.session_state.saved_quotes, quote
            )
            return quote

    def update_quote(self, quote_id: str, quote_input: QuoteInput, language: str):
        """Met à jour une citation existante."""
        quote = self.service.find_quote_by_id(st.session_state.quotes, quote_id)
        if quote:
            updated_quote = self.service.update_quote_from_input(
                quote, quote_input, language
            )
            # Remplacer dans la liste
            quotes = st.session_state.quotes.copy()
            for i, q in enumerate(quotes):
                if q.id == quote_id:
                    quotes[i] = updated_quote
                    break
            st.session_state.quotes = quotes

    def delete_quote(self, quote_id: str):
        """Supprime une citation."""
        st.session_state.quotes = self.service.remove_quote_by_id(
            st.session_state.quotes, quote_id
        )
        if self.current_quote and self.current_quote.id == quote_id:
            if st.session_state.quotes:
                self.current_quote = st.session_state.quotes[0]
            else:
                st.session_state.current_quote = None

    def get_random_quote(self, language: str = "fr") -> Optional[Quote]:
        """Retourne une citation aléatoire et la définit comme courante."""
        if USE_API_BACKEND and self._api_client:
            # Mode API
            quote = self._api_client.get_random_quote(language=language)
        else:
            # Mode direct
            quote = self.service.get_random_quote(self.quotes)

        if quote:
            self.current_quote = quote
        return quote

    def save_current_quote(self) -> bool:
        """Sauvegarde la citation courante."""
        if self.current_quote:
            saved_quotes, was_added = self.service.add_quote_if_not_exists(
                st.session_state.saved_quotes, self.current_quote
            )
            st.session_state.saved_quotes = saved_quotes
            return was_added
        return False

    def save_current_poem(self) -> bool:
        """Sauvegarde le poème courant."""
        if self.current_quote and self.current_quote.category == "poem":
            saved_poems, was_added = self.service.add_quote_if_not_exists(
                st.session_state.saved_poems, self.current_quote
            )
            st.session_state.saved_poems = saved_poems
            return was_added
        return False

    def export_saved_data(self) -> str:
        """Exporte les données sauvegardées au format JSON."""
        return self.service.export_quotes_to_json(self.saved_quotes, self.saved_poems)
