"""
Page rendering functions for the Streamlit application.
"""

from datetime import datetime

import streamlit as st

from ..config import (
    EXPORT_DATE_FORMAT,
    EXPORT_FILE_PREFIX,
    QUOTE_LIST_HEIGHT,
)
from ..core.haiku_adapter import HaikuAdapter
from ..core.quote_adapter import QuoteAdapter
from ..state_manager import StateManager
from ..ui_components import render_category_badge, render_quote_list_item
from .styles import (
    get_original_quote_html,
    get_quote_display_html,
    get_usage_display_html,
)


def render_current_quote(quote_manager: QuoteAdapter, lang: str, t: dict):
    """Affiche la citation courante."""
    if not quote_manager.current_quote:
        return

    current_quote = quote_manager.current_quote
    quote_text = quote_manager.get_text(current_quote.text, lang)
    quote_author = quote_manager.get_text(current_quote.author, lang)

    # Utiliser un conteneur Streamlit avec bordure
    with st.container(border=True):
        # Citation avec styles centralisés
        quote_html = get_quote_display_html(quote_text, quote_author)
        st.markdown(quote_html, unsafe_allow_html=True)

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
                    key=f"save_"
                    f"{'poem' if current_quote.category == 'poem' else 'quote'}",
                    use_container_width=True,
                ):
                    if current_quote.category == "poem":
                        quote_manager.save_current_poem()
                    else:
                        quote_manager.save_current_quote()
                    st.rerun()

    # Afficher la citation originale si c'est un haïku
    if current_quote.category == "poem" and quote_manager.original_quote:
        original = quote_manager.original_quote
        original_text = quote_manager.get_text(original.text, lang)
        original_author = quote_manager.get_text(original.author, lang)

        st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
        label = t.get(
            "original_quote", "Citation originale" if lang == "fr" else "Original quote"
        )
        original_html = get_original_quote_html(original_text, original_author, label)
        st.markdown(original_html, unsafe_allow_html=True)


def render_action_buttons(
    quote_manager: QuoteAdapter, haiku_generator: HaikuAdapter, lang: str, t: dict
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

    # Boutons pour haïku selon le contexte
    with col2:
        # Vérifier si on affiche un poème actuellement
        is_poem = (
            quote_manager.current_quote
            and quote_manager.current_quote.category == "poem"
        )

        # Si c'est déjà un poème, proposer de créer un nouveau
        if is_poem:
            # Vérifier si on a atteint la limite
            has_reached_limit = st.session_state.get("haiku_generation_count", 0) >= 5

            # Texte du bouton avec indication si limite atteinte
            button_text = f"✨ {t['create_poem']}"
            if has_reached_limit:
                button_text = f"🚫 {t.get('limit_reached', 'Limite atteinte')}"

            if st.button(
                button_text,
                key="create_new_poem",
                disabled=not quote_manager.current_quote or has_reached_limit,
                use_container_width=True,
                type="secondary",
            ):
                # Utiliser la citation originale si elle existe
                # Si on affiche déjà un poème, original_quote devrait toujours exister
                source_quote = quote_manager.original_quote
                if not source_quote:
                    # Fallback de sécurité - ne devrait jamais arriver
                    st.error("Erreur: citation originale non trouvée")
                    return

                with st.spinner(t["creating"]):
                    # Vérifier si l'API est disponible
                    if not haiku_generator.api_client:
                        st.error(
                            t.get(
                                "api_error",
                                "❌ Clé API non configurée. Impossible de générer de nouveaux haïkus.",
                            )
                        )
                        # Essayer de récupérer un haïku existant à la place
                        existing_poem = haiku_generator.get_existing_haiku(
                            source_quote, lang
                        )
                        if existing_poem:
                            quote_manager.current_quote = existing_poem
                            st.rerun()
                    else:
                        # Toujours forcer la création d'un nouveau haïku
                        poem = haiku_generator.generate_from_quote(
                            source_quote, lang, force_new=True
                        )
                        if poem:
                            quote_manager.current_quote = poem
                            st.rerun()
                        else:
                            # Si échec de génération, essayer de récupérer un haïku existant
                            existing_poem = haiku_generator.get_existing_haiku(
                                source_quote, lang
                            )
                            if existing_poem:
                                st.warning(
                                    t.get(
                                        "api_fail_fallback",
                                        "⚠️ Erreur API. Affichage d'un haïku existant.",
                                    )
                                )
                                quote_manager.current_quote = existing_poem
                                st.rerun()
        else:
            # Si c'est une citation, proposer de voir le haïku existant
            if st.button(
                f"👁️ {t.get('view_haiku', 'Voir le Haïku')}",
                key="view_haiku",
                disabled=not quote_manager.current_quote,
                use_container_width=True,
                type="secondary",
            ):
                with st.spinner(t.get("loading_haiku", "Chargement...")):
                    # Récupérer le haïku existant
                    poem = haiku_generator.get_existing_haiku(
                        quote_manager.current_quote, lang
                    )
                    if poem:
                        # Sauvegarder la citation originale
                        quote_manager.original_quote = quote_manager.current_quote
                        quote_manager.current_quote = poem
                        st.rerun()
                    else:
                        st.info(
                            t.get(
                                "no_haiku",
                                "Aucun haïku disponible pour cette citation.",
                            )
                        )

    # Voir toutes les citations
    with col3:
        show_all = StateManager.get_show_all_quotes()
        if st.button(
            f"📋 {t['hide'] if show_all else t['show_all']} "
            f"({len(quote_manager.quotes)})",
            key="show_all_btn",
            use_container_width=True,
        ):
            StateManager.toggle_show_all_quotes()
            st.rerun()

    # Afficher le compteur d'usage si API disponible
    if haiku_generator.api_client:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        usage_display = haiku_generator.get_usage_display(lang)
        usage_html = get_usage_display_html(usage_display)
        st.markdown(usage_html, unsafe_allow_html=True)

    # Afficher un message sympathique si la limite est atteinte
    if st.session_state.get("haiku_generation_count", 0) >= 5:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        st.info(
            t.get(
                "limit_message",
                "🐝 Les haïkus sont plus savoureux avec modération. Revenez demain pour 5 nouvelles créations !",
            )
        )

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


def render_all_quotes_list(quote_manager: QuoteAdapter, lang: str, t: dict):
    """Affiche la liste de toutes les citations."""
    if not StateManager.get_show_all_quotes():
        return

    st.markdown("<br>", unsafe_allow_html=True)

    container = st.container(height=QUOTE_LIST_HEIGHT)
    with container:
        for quote in quote_manager.quotes:
            quote_text = quote_manager.get_text(quote.text, lang)
            quote_author = quote_manager.get_text(quote.author, lang)

            render_quote_list_item(
                quote=quote,
                lang=lang,
                quote_text=quote_text,
                quote_author=quote_author,
                on_display=lambda q: (
                    setattr(quote_manager, "current_quote", q),
                    StateManager.hide_all_quotes(),
                    st.rerun(),
                ),
                on_delete=None,  # Suppression désactivée
            )
            st.divider()
