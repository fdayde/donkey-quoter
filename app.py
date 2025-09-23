"""
Donkey Quoter - Application Streamlit principale avec composants unifiés.
"""

from pathlib import Path

import streamlit as st

from src.donkey_quoter import __version__
from src.donkey_quoter.config.settings import settings
from src.donkey_quoter.core.haiku_adapter import HaikuAdapter
from src.donkey_quoter.core.quote_adapter import QuoteAdapter
from src.donkey_quoter.state_manager import StateManager
from src.donkey_quoter.translations import TRANSLATIONS

# UI Components - Composants UI consolidés
from src.donkey_quoter.ui.components import (
    render_action_bar,
    render_app_footer,
    render_app_header,
    render_quote_card,
    render_quote_list,
)


def load_css():
    """Charge les fichiers CSS personnalisés et les styles unifiés."""
    # CSS personnalisé existant
    if settings.paths.styles_css_path.exists():
        with open(settings.paths.styles_css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_services() -> tuple[QuoteAdapter, HaikuAdapter]:
    """Initialize core services."""
    quote_manager = QuoteAdapter()
    haiku_generator = HaikuAdapter(Path("data"))
    return quote_manager, haiku_generator


def handle_session_refresh():
    """Handle F5 refresh vs internal rerun."""
    if "session_id" not in st.session_state:
        import random
        import time

        st.session_state.session_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        if "current_quote" in st.session_state:
            del st.session_state.current_quote

    session_param = st.query_params.get("session")
    if session_param != st.session_state.session_id:
        if "current_quote" in st.session_state:
            del st.session_state.current_quote
        st.query_params["session"] = st.session_state.session_id


def main():
    """Point d'entrée principal de l'application avec composants unifiés."""
    # Configuration
    page_config = {
        "page_title": settings.app.page_title,
        "page_icon": settings.app.page_icon,
        "layout": settings.app.layout,
        "initial_sidebar_state": settings.app.initial_sidebar_state,
    }
    st.set_page_config(**page_config)
    handle_session_refresh()
    StateManager.initialize()
    load_css()

    # Initialisation
    quote_manager, haiku_generator = init_services()
    lang = StateManager.get_language()
    t = TRANSLATIONS[lang]

    # Header avec composants unifiés
    render_app_header(
        title=t["title"],
        lang=lang,
        on_language_change=lambda: (StateManager.toggle_language(), st.rerun()),
    )

    # Corps principal avec composants unifiés
    if quote_manager.current_quote:
        render_quote_card(
            quote=quote_manager.current_quote,
            quote_manager=quote_manager,
            lang=lang,
            t=t,
            with_actions=False,
            with_category_badge=False,
        )

    render_action_bar(quote_manager, haiku_generator, lang, t)

    # Liste des citations avec composants unifiés
    render_quote_list(quote_manager.quotes, quote_manager, lang, t)

    # Footer avec composants unifiés
    contribute_message = t.get(
        "contribute_message",
        "Venez ajouter vos propres citations"
        if lang == "fr"
        else "Come add your own quotes",
    )
    render_app_footer(__version__, contribute_message)


if __name__ == "__main__":
    main()
