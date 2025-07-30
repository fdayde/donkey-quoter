"""
Module de gestion des citations.
"""
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

from .data import CLASSIC_QUOTES
from .models import Quote, QuoteInput


class QuoteManager:
    """Gestionnaire des citations."""

    def __init__(self):
        """Initialise le gestionnaire de citations."""
        if "quotes" not in st.session_state:
            st.session_state.quotes = [Quote(**q) for q in CLASSIC_QUOTES]
        if "current_quote" not in st.session_state:
            st.session_state.current_quote = st.session_state.quotes[0]
        if "saved_quotes" not in st.session_state:
            st.session_state.saved_quotes = []
        if "saved_poems" not in st.session_state:
            st.session_state.saved_poems = []

    @property
    def quotes(self) -> List[Quote]:
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
    def saved_quotes(self) -> List[Quote]:
        """Retourne les citations sauvegardées."""
        return st.session_state.saved_quotes

    @property
    def saved_poems(self) -> List[Quote]:
        """Retourne les poèmes sauvegardés."""
        return st.session_state.saved_poems

    def get_text(self, text_dict: Dict[str, str], language: str) -> str:
        """Obtient le texte dans la langue spécifiée."""
        if isinstance(text_dict, dict):
            return text_dict.get(language, text_dict.get("fr", ""))
        return str(text_dict)

    def add_quote(self, quote_input: QuoteInput, language: str) -> Quote:
        """Ajoute une nouvelle citation."""
        quote = Quote(
            id=f"user_{int(datetime.now().timestamp())}",
            text={
                language: quote_input.text,
                "fr" if language == "en" else "en": quote_input.text,
            },
            author={
                language: quote_input.author,
                "fr" if language == "en" else "en": quote_input.author,
            },
            category=quote_input.category,
            type="user",
        )
        st.session_state.quotes.insert(0, quote)
        self.current_quote = quote
        # Sauvegarder automatiquement
        st.session_state.saved_quotes.append(quote)
        return quote

    def update_quote(self, quote_id: str, quote_input: QuoteInput, language: str):
        """Met à jour une citation existante."""
        for i, quote in enumerate(st.session_state.quotes):
            if quote.id == quote_id:
                quote.text[language] = quote_input.text
                quote.text["fr" if language == "en" else "en"] = quote_input.text
                quote.author[language] = quote_input.author
                quote.author["fr" if language == "en" else "en"] = quote_input.author
                quote.category = quote_input.category
                st.session_state.quotes[i] = quote
                break

    def delete_quote(self, quote_id: str):
        """Supprime une citation."""
        st.session_state.quotes = [q for q in st.session_state.quotes if q.id != quote_id]
        if self.current_quote and self.current_quote.id == quote_id:
            if st.session_state.quotes:
                self.current_quote = st.session_state.quotes[0]
            else:
                st.session_state.current_quote = None

    def get_random_quote(self) -> Optional[Quote]:
        """Retourne une citation aléatoire."""
        if self.quotes:
            quote = random.choice(self.quotes)
            self.current_quote = quote
            return quote
        return None

    def save_current_quote(self) -> bool:
        """Sauvegarde la citation courante."""
        if self.current_quote and self.current_quote not in st.session_state.saved_quotes:
            st.session_state.saved_quotes.append(self.current_quote)
            return True
        return False

    def save_current_poem(self) -> bool:
        """Sauvegarde le poème courant."""
        if (
            self.current_quote
            and self.current_quote.category == "poem"
            and self.current_quote not in st.session_state.saved_poems
        ):
            st.session_state.saved_poems.append(self.current_quote)
            return True
        return False

    def export_saved_data(self) -> str:
        """Exporte les données sauvegardées au format JSON."""
        data = {
            "savedQuotes": [q.model_dump() for q in self.saved_quotes],
            "savedPoems": [p.model_dump() for p in self.saved_poems],
            "exportDate": datetime.now().isoformat(),
            "totalSavedQuotes": len(self.saved_quotes),
            "totalSavedPoems": len(self.saved_poems),
        }
        return json.dumps(data, ensure_ascii=False, indent=2)