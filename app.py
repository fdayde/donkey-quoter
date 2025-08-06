"""
Donkey Quoter - Application Streamlit principale (version refactorisée).
"""

from pathlib import Path

import streamlit as st

from src.donkey_quoter import __version__
from src.donkey_quoter.config import PAGE_CONFIG, STYLES_CSS_PATH
from src.donkey_quoter.core.haiku_adapter import HaikuAdapter
from src.donkey_quoter.core.quote_adapter import QuoteAdapter
from src.donkey_quoter.state_manager import StateManager
from src.donkey_quoter.translations import TRANSLATIONS
from src.donkey_quoter.ui.pages import (
    render_action_buttons,
    render_all_quotes_list,
    render_current_quote,
)
from src.donkey_quoter.ui.styles import get_footer_html
from src.donkey_quoter.ui_components import render_header


def load_css():
    """Charge les fichiers CSS personnalisés."""
    if STYLES_CSS_PATH.exists():
        with open(STYLES_CSS_PATH) as f:
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
    """Point d'entrée principal de l'application."""
    # Configuration
    st.set_page_config(**PAGE_CONFIG)
    handle_session_refresh()
    StateManager.initialize()
    load_css()

    # Initialisation
    quote_manager, haiku_generator = init_services()
    lang = StateManager.get_language()
    t = TRANSLATIONS[lang]

    # Header
    render_header(
        title=t["title"],
        subtitle=t["subtitle"],
        lang=lang,
        on_language_change=lambda: (StateManager.toggle_language(), st.rerun()),
    )

    # Corps principal
    render_current_quote(quote_manager, lang, t)
    render_action_buttons(quote_manager, haiku_generator, lang, t)

    if StateManager.get_show_all_quotes():
        render_all_quotes_list(quote_manager, lang, t)

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    contribute_message = t.get(
        "contribute_message",
        "Venez ajouter vos propres citations"
        if lang == "fr"
        else "Come add your own quotes",
    )
    footer_html = get_footer_html(__version__, contribute_message)
    st.markdown(footer_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
