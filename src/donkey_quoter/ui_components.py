"""
Composants UI réutilisables pour l'application Streamlit.
"""

from typing import Callable, Optional

import streamlit as st

from .models import Quote
from .translations import CATEGORY_LABELS, TRANSLATIONS
from .ui.styles import (
    get_category_badge_html,
    get_header_style,
    get_quote_list_item_html,
)


def render_category_badge(category: str, lang: str):
    """Affiche un badge de catégorie."""
    category_label = CATEGORY_LABELS.get(category, {}).get(lang, category)
    badge_html = get_category_badge_html(category_label, category)
    st.markdown(badge_html, unsafe_allow_html=True)


def render_stats_card(value: int, label: str, style_class: str = ""):
    """Affiche une carte de statistiques."""
    st.markdown(
        f'<div class="stats-card {style_class}">'
        f'<div class="stats-number">{value}</div>'
        f'<div class="stats-label">{label}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_action_button(
    label: str,
    key: str,
    on_click: Optional[Callable] = None,
    disabled: bool = False,
    use_container_width: bool = True,
) -> bool:
    """Crée un bouton d'action standardisé."""
    return st.button(
        label,
        key=key,
        disabled=disabled,
        use_container_width=use_container_width,
        on_click=on_click,
    )


def render_header(title: str, subtitle: str, lang: str, on_language_change: Callable):
    """Affiche l'en-tête de l'application."""
    # Créer un conteneur pour le header complet
    header_container = st.container()

    with header_container:
        # Ligne avec emoji âne au centre et bouton langue à droite
        col1, col2, col3 = st.columns([2, 6, 2])

        # Colonne centrale avec l'emoji âne
        with col2:
            st.markdown(
                '<div style="text-align: center; font-size: 5rem; '
                'margin-bottom: -2.5rem;">🫏</div>',
                unsafe_allow_html=True,
            )

        # Colonne de droite avec le bouton langue (aligné verticalement avec l'âne)
        with col3:
            st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
            if st.button(
                f"🌐 {'EN' if lang == 'fr' else 'FR'}",
                key="lang_switch",
                use_container_width=False,
            ):
                on_language_change()

        # Titre et sous-titre centrés avec styles
        header_html = get_header_style(title, subtitle)
        st.markdown(header_html, unsafe_allow_html=True)


def render_quote_list_item(
    quote: Quote,
    lang: str,
    quote_text: str,
    quote_author: str,
    on_display: Callable,
    on_delete: Optional[Callable] = None,
):
    """Affiche un élément dans la liste des citations."""
    col1, col2 = st.columns([5, 1])

    with col1:
        render_category_badge(quote.category, lang)
        quote_html = get_quote_list_item_html(quote_text, quote_author)
        st.markdown(quote_html, unsafe_allow_html=True)

    with col2:
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button(
                "👁", key=f"display_{quote.id}", help=TRANSLATIONS[lang]["display"]
            ):
                on_display(quote)

        if quote.type == "user" and on_delete:
            with button_col2:
                if st.button(
                    "🗑", key=f"delete_{quote.id}", help=TRANSLATIONS[lang]["delete"]
                ):
                    on_delete(quote.id)
