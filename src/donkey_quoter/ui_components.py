"""
Composants UI réutilisables pour l'application Streamlit.
"""
from typing import Dict, Optional, Callable
import streamlit as st
from .models import Quote
from .translations import CATEGORY_LABELS


CATEGORY_COLORS = {
    "classic": "orange",
    "personal": "orange", 
    "poem": "red",
    "humor": "yellow"
}




def render_category_badge(category: str, lang: str):
    """Affiche un badge de catégorie."""
    category_label = CATEGORY_LABELS.get(category, {}).get(lang, category)
    color = CATEGORY_COLORS.get(category, "gray")
    st.badge(category_label, color=color)


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
    use_container_width: bool = True
) -> bool:
    """Crée un bouton d'action standardisé."""
    return st.button(
        label,
        key=key,
        disabled=disabled,
        use_container_width=use_container_width,
        on_click=on_click
    )


def render_header(title: str, subtitle: str, lang: str, on_language_change: Callable):
    """Affiche l'en-tête de l'application."""
    # Bouton langue
    col1, col2 = st.columns([5, 1])
    with col2:
        st.markdown(
            """
            <style>
            div[data-testid="column"]:last-child {
                text-align: right;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button(
            f"🌐 {'EN' if lang == 'fr' else 'FR'}",
            key="lang_switch",
            help=TRANSLATIONS[lang]["language"],
            use_container_width=True,
        ):
            on_language_change()
    
    # Header centré
    st.markdown(
        '<div class="main-header">'
        '<div class="donkey-emoji">🫏</div>'
        f'<h1 style="font-size: 1.875rem; font-weight: 300; color: rgba(120, 53, 15, 0.9); letter-spacing: 0.05em;">{title}</h1>'
        f'<p style="color: rgba(180, 83, 9, 0.7); font-size: 0.875rem; font-weight: 300;">{subtitle}</p>'
        "</div>",
        unsafe_allow_html=True,
    )


def render_quote_list_item(
    quote: Quote,
    lang: str,
    quote_text: str,
    quote_author: str,
    on_display: Callable,
    on_delete: Optional[Callable] = None
):
    """Affiche un élément dans la liste des citations."""
    col1, col2 = st.columns([5, 1])
    
    with col1:
        render_category_badge(quote.category, lang)
        st.markdown(
            f'<p style="margin: 0.5rem 0; color: rgba(120, 53, 15, 0.7); font-size: 0.875rem;">'
            f'"{quote_text}"</p>'
            f'<p style="margin: 0; color: rgba(180, 83, 9, 0.6); font-size: 0.75rem;">— {quote_author}</p>',
            unsafe_allow_html=True,
        )
    
    with col2:
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("👁", key=f"display_{quote.id}", help=TRANSLATIONS[lang]["display"]):
                on_display(quote)
        
        if quote.type == "user" and on_delete:
            with button_col2:
                if st.button("🗑", key=f"delete_{quote.id}", help=TRANSLATIONS[lang]["delete"]):
                    on_delete(quote.id)


# Import pour éviter les imports circulaires
from .translations import TRANSLATIONS