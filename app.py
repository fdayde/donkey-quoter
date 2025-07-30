"""
Donkey Quoter - Application Streamlit principale (version refactorisée).
"""
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.donkey_quoter.config import (
    PAGE_CONFIG, STYLES_CSS_PATH,
    QUOTE_LIST_HEIGHT, EXPORT_DATE_FORMAT, EXPORT_FILE_PREFIX
)
from src.donkey_quoter.haiku_generator import HaikuGenerator
from src.donkey_quoter.models import QuoteInput
from src.donkey_quoter.quote_manager import QuoteManager
from src.donkey_quoter.state_manager import StateManager
from src.donkey_quoter.translations import TRANSLATIONS
from src.donkey_quoter.ui_components import (
    render_header, render_category_badge,
    render_stats_card, render_quote_list_item
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
        # Citation avec style centré
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1.5rem 0;">
                <div style="font-size: 3rem; color: #fcd34d; margin-bottom: 0.75rem;">"</div>
                <div style="font-size: 1.5rem; color: rgba(120, 53, 15, 0.9); line-height: 1.8; font-weight: 300; white-space: pre-line; margin-bottom: 1rem;">
                    {quote_text}
                </div>
                <div style="color: rgba(180, 83, 9, 0.7); font-size: 1rem; font-weight: 500;">
                    — {quote_author}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Badge de catégorie et bouton sauvegarde
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                render_category_badge(current_quote.category, lang)
            
            with subcol2:
                save_list = (quote_manager.saved_poems if current_quote.category == "poem" 
                            else quote_manager.saved_quotes)
                is_saved = current_quote in save_list
                
                if st.button(
                    f"💾 {t['saved'] if is_saved else t['save']}",
                    disabled=is_saved,
                    key=f"save_{'poem' if current_quote.category == 'poem' else 'quote'}",
                    use_container_width=True,
                ):
                    if current_quote.category == "poem":
                        quote_manager.save_current_poem()
                    else:
                        quote_manager.save_current_quote()
                    st.rerun()


def render_action_buttons(quote_manager: QuoteManager, haiku_generator: HaikuGenerator, lang: str, t: dict):
    """Affiche les boutons d'action principaux."""
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4, gap="small")
    
    # Nouvelle citation
    with col1:
        if st.button(f"🔀 {t['new_quote']}", key="new_quote", use_container_width=True):
            quote_manager.get_random_quote()
            st.rerun()
    
    # Créer haïku
    with col2:
        if st.button(
            f"✨ {t['create_poem']}",
            key="create_poem",
            disabled=not quote_manager.current_quote,
            use_container_width=True,
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
    
    # Exporter
    with col4:
        total_saved = len(quote_manager.saved_quotes) + len(quote_manager.saved_poems)
        if total_saved > 0:
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
                        st.rerun()
                    ),
                    on_delete=lambda qid: (
                        quote_manager.delete_quote(qid),
                        st.rerun()
                    ) if quote.type == "user" else None
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
        render_stats_card(
            len(quote_manager.saved_quotes),
            t["saved_quotes"]
        )
    with col2:
        render_stats_card(
            len(quote_manager.saved_poems),
            t["saved_poems"],
            style_class="rose"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_add_quote_form(quote_manager: QuoteManager, lang: str, t: dict):
    """Affiche le formulaire d'ajout de citation."""
    from src.donkey_quoter.translations import CATEGORY_LABELS
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander(f"➕ {t['add_quote']}", expanded=False):
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
            
            submitted = st.form_submit_button(t["add"], use_container_width=True)
            if submitted:
                if text and author:
                    quote_input = QuoteInput(
                        text=text.strip(),
                        author=author.strip(),
                        category=category,
                    )
                    quote_manager.add_quote(quote_input, lang)
                    st.success("✅")
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
        on_language_change=lambda: (StateManager.toggle_language(), st.rerun())
    )
    
    # Citation courante
    render_current_quote(quote_manager, lang, t)
    
    # Boutons d'action
    render_action_buttons(quote_manager, haiku_generator, lang, t)
    
    # Liste des citations
    render_all_quotes_list(quote_manager, lang, t)
    
    # Statistiques
    render_saved_stats(quote_manager, t)
    
    # Formulaire d'ajout
    render_add_quote_form(quote_manager, lang, t)


if __name__ == "__main__":
    main()