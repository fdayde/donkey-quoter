"""
Adaptateur pour utiliser QuoteService avec l'interface de QuoteManager existante.
"""

from typing import Optional

import streamlit as st

from .models import Quote, QuoteInput
from .quote_service import QuoteService


class QuoteAdapter:
    """Adaptateur qui utilise QuoteService mais maintient l'interface de QuoteManager."""

    def __init__(self):
        """Initialise l'adaptateur avec le service."""
        self.service = QuoteService()
        # Initialiser le state si nécessaire (comme le faisait QuoteManager)
        if "quotes" not in st.session_state:
            from ..data import CLASSIC_QUOTES

            st.session_state.quotes = [Quote(**q) for q in CLASSIC_QUOTES]
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
        return self.service.get_text(text_dict, language)

    def add_quote(self, quote_input: QuoteInput, language: str) -> Quote:
        """Ajoute une nouvelle citation."""
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

    def get_random_quote(self) -> Optional[Quote]:
        """Retourne une citation aléatoire et la définit comme courante."""
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
