"""
Gestionnaire d'état centralisé pour l'application.
"""

import streamlit as st

from .core.models import Quote
from .data import CLASSIC_QUOTES


class StateManager:
    """Gère l'état de l'application de manière centralisée."""

    @staticmethod
    def initialize():
        """Initialise l'état de l'application."""
        import random

        if "quotes" not in st.session_state:
            st.session_state.quotes = [Quote(**q) for q in CLASSIC_QUOTES]

        # Toujours choisir une citation aléatoire si current_quote n'existe pas
        # Cela permet d'avoir une nouvelle citation à chaque refresh complet (F5)
        if "current_quote" not in st.session_state:
            st.session_state.current_quote = random.choice(st.session_state.quotes)

        if "saved_quotes" not in st.session_state:
            st.session_state.saved_quotes = []
        if "saved_poems" not in st.session_state:
            st.session_state.saved_poems = []
        if "language" not in st.session_state:
            st.session_state.language = "fr"
        if "show_all_quotes" not in st.session_state:
            st.session_state.show_all_quotes = False

    @staticmethod
    def get_language() -> str:
        """Retourne la langue actuelle."""
        return st.session_state.language

    @staticmethod
    def toggle_language():
        """Change la langue de l'application."""
        st.session_state.language = "en" if st.session_state.language == "fr" else "fr"

    @staticmethod
    def get_show_all_quotes() -> bool:
        """Retourne l'état d'affichage de toutes les citations."""
        return st.session_state.get("show_all_quotes", False)

    @staticmethod
    def toggle_show_all_quotes():
        """Bascule l'affichage de toutes les citations."""
        st.session_state.show_all_quotes = not st.session_state.get(
            "show_all_quotes", False
        )

    @staticmethod
    def set_current_quote(quote: Quote):
        """Définit la citation courante."""
        st.session_state.current_quote = quote

    @staticmethod
    def hide_all_quotes():
        """Cache la liste de toutes les citations."""
        st.session_state.show_all_quotes = False
