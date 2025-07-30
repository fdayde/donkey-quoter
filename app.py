"""
Donkey Quoter - Application Streamlit principale (version refactorisée).
"""

from datetime import datetime
from pathlib import Path

import streamlit as st

from src.donkey_quoter.config import (
    PAGE_CONFIG,
    STYLES_CSS_PATH,
    QUOTE_LIST_HEIGHT,
    EXPORT_DATE_FORMAT,
    EXPORT_FILE_PREFIX,
)
from src.donkey_quoter.haiku_generator import HaikuGenerator
from src.donkey_quoter.models import QuoteInput
from src.donkey_quoter.quote_manager import QuoteManager
from src.donkey_quoter.state_manager import StateManager
from src.donkey_quoter.translations import TRANSLATIONS
from src.donkey_quoter.ui_components import (
    render_header,
    render_category_badge,
    render_stats_card,
    render_quote_list_item,
)


def load_css():
    """Charge les fichiers CSS personnalisés."""
    if STYLES_CSS_PATH.exists():
        with open(STYLES_CSS_PATH) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_current_quote(quote_manager: QuoteManager, lang: str, t: dict):
    """Affiche la citation courante."""
    if not quote_manager.current_quote:
        return

    current_quote = quote_manager.current_quote
    quote_text = quote_manager.get_text(current_quote.text, lang)
    quote_author = quote_manager.get_text(current_quote.author, lang)

    # Utiliser un conteneur Streamlit avec bordure
    with st.container(border=True):
        # Citation avec guillemet stylisé (seulement ouvrant)
        st.markdown(
            f"""
            <div style="padding: 2rem;">
                <div style="text-align: center; margin-bottom: -1.5rem;">
                    <span style="font-size: 4rem; color: #d97706; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 0.5;">"</span>
                </div>
                <div style="font-size: 1.25rem; color: #78350f; line-height: 1.8; font-weight: 300; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; text-align: center; margin: 0 2rem; white-space: pre-line;">
                    {quote_text}
                </div>
                <div style="text-align: right; margin-right: 2rem; margin-top: 1rem;">
                    <span style="color: #b45309; font-size: 0.75rem; font-weight: 500; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">— {quote_author}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tags/Catégories sous l'attribution
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                render_category_badge(current_quote.category, lang)

            with subcol2:
                save_list = (
                    quote_manager.saved_poems
                    if current_quote.category == "poem"
                    else quote_manager.saved_quotes
                )
                is_saved = current_quote in save_list

                # Bouton Sauvegarder avec style jaune/doré
                if st.button(
                    f"{t['saved'] if is_saved else t['save']}",
                    disabled=is_saved,
                    key=f"save_{'poem' if current_quote.category == 'poem' else 'quote'}",
                    use_container_width=True,
                ):
                    if current_quote.category == "poem":
                        quote_manager.save_current_poem()
                    else:
                        quote_manager.save_current_quote()
                    st.rerun()


def render_action_buttons(
    quote_manager: QuoteManager, haiku_generator: HaikuGenerator, lang: str, t: dict
):
    """Affiche les boutons d'action principaux."""
    st.markdown("<br>", unsafe_allow_html=True)

    # Boutons principaux en ligne horizontale (3 colonnes)
    col1, col2, col3 = st.columns(3, gap="medium")

    # Nouvelle citation
    with col1:
        if st.button(
            f"🔀 {t['new_quote']}",
            key="new_quote",
            use_container_width=True,
            type="primary",
        ):
            quote_manager.get_random_quote()
            st.rerun()

    # Créer haïku
    with col2:
        if st.button(
            f"✨ {t['create_poem']}",
            key="create_poem",
            disabled=not quote_manager.current_quote,
            use_container_width=True,
            type="secondary",
        ):
            with st.spinner(t["creating"]):
                poem = haiku_generator.generate_from_quote(
                    quote_manager.current_quote, lang
                )
                if poem:
                    quote_manager.current_quote = poem
                    st.rerun()

    # Voir toutes les citations
    with col3:
        show_all = StateManager.get_show_all_quotes()
        if st.button(
            f"📋 {t['hide'] if show_all else t['show_all']} ({len(quote_manager.quotes)})",
            key="show_all_btn",
            use_container_width=True,
        ):
            StateManager.toggle_show_all_quotes()
            st.rerun()

    # Bouton secondaire centré (Ajouter une citation)
    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            f"➕ {t['add_quote']}",
            key="add_quote_btn",
            use_container_width=True,
            type="primary",
        ):
            if "show_add_form" not in st.session_state:
                st.session_state.show_add_form = False
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.rerun()

    # Bouton Export (si des citations sont sauvegardées)
    total_saved = len(quote_manager.saved_quotes) + len(quote_manager.saved_poems)
    if total_saved > 0:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            export_data = quote_manager.export_saved_data()
            st.download_button(
                label=f"📥 {t['export']} ({total_saved})",
                data=export_data,
                file_name=f"{EXPORT_FILE_PREFIX}-{datetime.now().strftime(EXPORT_DATE_FORMAT)}.json",
                mime="application/json",
                key="export",
                use_container_width=True,
            )


def render_all_quotes_list(quote_manager: QuoteManager, lang: str, t: dict):
    """Affiche la liste de toutes les citations."""
    if not StateManager.get_show_all_quotes():
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="quote-card">', unsafe_allow_html=True)

    container = st.container(height=QUOTE_LIST_HEIGHT)
    with container:
        for quote in quote_manager.quotes:
            with st.container():
                quote_text = quote_manager.get_text(quote.text, lang)
                quote_author = quote_manager.get_text(quote.author, lang)

                render_quote_list_item(
                    quote=quote,
                    lang=lang,
                    quote_text=quote_text,
                    quote_author=quote_author,
                    on_display=lambda q: (
                        quote_manager.set_current_quote(q),
                        StateManager.hide_all_quotes(),
                        st.rerun(),
                    ),
                    on_delete=lambda qid: (
                        (quote_manager.delete_quote(qid), st.rerun())
                        if quote.type == "user"
                        else None
                    ),
                )
                st.divider()

    st.markdown("</div>", unsafe_allow_html=True)


def render_saved_stats(quote_manager: QuoteManager, t: dict):
    """Affiche les statistiques de sauvegarde."""
    if not (quote_manager.saved_quotes or quote_manager.saved_poems):
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="quote-card">', unsafe_allow_html=True)
    st.markdown(
        f'<h3 style="text-align: center; font-weight: 300; color: rgba(120, 53, 15, 0.9);">{t["my_saves"]}</h3>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        render_stats_card(len(quote_manager.saved_quotes), t["saved_quotes"])
    with col2:
        render_stats_card(
            len(quote_manager.saved_poems), t["saved_poems"], style_class="rose"
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_add_quote_form(quote_manager: QuoteManager, lang: str, t: dict):
    """Affiche le formulaire d'ajout de citation."""
    from src.donkey_quoter.translations import CATEGORY_LABELS

    if st.session_state.get("show_add_form", False):
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"### {t['add_quote']}")
            with st.form("add_quote_form", clear_on_submit=True):
                text = st.text_area(
                    t["citation"],
                    placeholder=t["placeholder_quote"],
                    height=100,
                )
                author = st.text_input(
                    t["author"],
                    placeholder=t["placeholder_author"],
                )
                category = st.selectbox(
                    t["category"],
                    options=["personal", "humor", "classic"],
                    format_func=lambda x: CATEGORY_LABELS[x][lang],
                )

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button(
                        t["add"], use_container_width=True, type="primary"
                    )
                with col2:
                    if st.form_submit_button(
                        t.get("cancel", "Annuler"), use_container_width=True
                    ):
                        st.session_state.show_add_form = False
                        st.rerun()

                if submitted:
                    if text and author:
                        quote_input = QuoteInput(
                            text=text.strip(),
                            author=author.strip(),
                            category=category,
                        )
                        quote_manager.add_quote(quote_input, lang)
                        st.success("✅")
                        st.session_state.show_add_form = False
                        st.rerun()
                    else:
                        st.error("❌")


def main():
    """Point d'entrée principal de l'application."""
    # Configuration de la page
    st.set_page_config(**PAGE_CONFIG)

    # Initialiser l'état
    StateManager.initialize()

    # Charger le CSS
    load_css()

    # Initialiser les gestionnaires
    quote_manager = QuoteManager()
    haiku_generator = HaikuGenerator()

    # Obtenir la langue et les traductions
    lang = StateManager.get_language()
    t = TRANSLATIONS[lang]

    # En-tête
    render_header(
        title=t["title"],
        subtitle=t["subtitle"],
        lang=lang,
        on_language_change=lambda: (StateManager.toggle_language(), st.rerun()),
    )

    # Citation courante
    render_current_quote(quote_manager, lang, t)

    # Boutons d'action
    render_action_buttons(quote_manager, haiku_generator, lang, t)

    # Formulaire d'ajout (affiché sous le bouton Ajouter)
    render_add_quote_form(quote_manager, lang, t)

    # Liste des citations
    render_all_quotes_list(quote_manager, lang, t)

    # Statistiques
    render_saved_stats(quote_manager, t)

    # Footer avec lien GitHub
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0 1rem 0; border-top: 1px solid rgba(254, 243, 199, 0.5); margin-top: 3rem;">
            <a href="https://github.com/fdayde/donkey-quoter" target="_blank" style="color: #d97706; text-decoration: none; font-size: 0.875rem;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: middle; margin-right: 0.5rem;">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
