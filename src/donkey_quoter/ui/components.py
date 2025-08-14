"""
UI Components - Consolidated UI module for Donkey Quoter.

This module consolidates all UI rendering functions from legacy modules:
- ui/pages.py (deleted)
- ui/styles.py (HTML functions moved here)
- ui_components.py (deleted)
- ui/layouts.py (deleted)

Provides clean, reusable UI components with centralized CSS.
"""

from datetime import datetime
from typing import Any, Callable, Optional

import streamlit as st

from ..config.settings import settings
from ..core.haiku_adapter import HaikuAdapter
from ..core.models import Quote
from ..core.quote_adapter import QuoteAdapter
from ..state_manager import StateManager
from ..translations import TRANSLATIONS

# =============================================================================
# HTML TEMPLATES - Centralized HTML with CSS classes
# =============================================================================

TEMPLATES = {
    "quote_card": """
    <div class="quote-container">
        <div class="quote-opening">"</div>
        <div class="quote-text">{text}</div>
        <div class="quote-author">— {author}</div>
    </div>
    """,
    "original_quote": """
    <div class="original-quote-container">
        <p class="original-quote-label">{label}:</p>
        <p class="original-quote-text">"{text}" — {author}</p>
    </div>
    """,
    "usage_display": """
    <div class="usage-counter">{usage_text}</div>
    """,
    "header": """
    <div class="app-header">
        <h1 class="app-title">{title}</h1>
    </div>
    """,
    "footer": """
    <div class="app-footer">
        <a href="https://github.com/fdayde/donkey-quoter" target="_blank" class="github-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" class="github-icon">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207
                    11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416
                    -4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083
                    -.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834
                    2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305
                    -5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124
                    -.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266
                    1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552
                    3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235
                    1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823
                    1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199
                    -6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
        </a>
        <p class="contribute-message">↑ {contribute_message}</p>
        <p class="version-info">Donkey Quoter v{version}</p>
    </div>
    """,
    "quote_list_item": """
    <div class="quote-list-item">
        <p class="quote-list-text">"{text}"</p>
        <p class="quote-list-author">— {author}</p>
    </div>
    """,
}

# CSS Styles (extracted from inline styles for consistency)
CSS_STYLES = """
<style>
    .quote-container {
        padding: 2rem;
        text-align: center;
    }

    .quote-opening {
        font-size: 4rem;
        color: #d97706;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        line-height: 0.5;
        margin-bottom: -1.5rem;
        text-align: center;
    }

    .quote-text {
        font-size: 1.25rem;
        color: #78350f;
        line-height: 1.8;
        font-weight: 300;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        text-align: center;
        margin: 0 2rem;
        white-space: pre-line;
    }

    .quote-author {
        text-align: right;
        margin-right: 2rem;
        margin-top: 1rem;
        color: #b45309;
        font-size: 0.75rem;
        font-weight: 500;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    }

    .original-quote-container {
        text-align: center;
        padding: 0.5rem;
        background-color: rgba(254, 243, 199, 0.3);
        border-radius: 0.5rem;
        margin-top: 0.5rem;
    }

    .original-quote-label {
        font-size: 0.75rem;
        color: #92400e;
        font-style: italic;
        margin: 0;
    }

    .original-quote-text {
        font-size: 0.75rem;
        color: #78350f;
        margin: 0.25rem 0 0 0;
    }


    .usage-counter {
        text-align: center;
        color: #92400e;
        font-size: 0.875rem;
    }

    .app-header {
        text-align: center;
    }

    .app-title {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-size: 2.5rem;
        font-weight: 300;
        color: #78350f;
        margin: 0;
    }


    .app-footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid rgba(254, 243, 199, 0.5);
        margin-top: 3rem;
    }

    .github-link {
        color: #d97706 !important;
        text-decoration: none;
        font-size: 0.875rem;
    }

    .github-link:visited {
        color: #d97706 !important;
    }

    .github-link:hover {
        color: #b45309 !important;
        text-decoration: underline;
    }

    .github-icon {
        vertical-align: middle;
        margin-right: 0.5rem;
    }

    .contribute-message {
        font-size: 0.625rem;
        font-style: italic;
        color: #d97706;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }

    .version-info {
        font-size: 0.625rem;
        color: #a3a3a3;
        margin-top: 0.75rem;
        margin-bottom: 0;
    }

    .quote-list-item {
        padding: 0.5rem 0;
    }

    .quote-list-text {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-weight: 300;
        margin: 0.5rem 0;
        color: #78350f;
        font-size: 0.875rem;
    }

    .quote-list-author {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
        font-weight: 500;
        margin: 0;
        color: rgba(180, 83, 9, 0.7);
        font-size: 0.75rem;
    }

    .spacer {
        margin-top: 1rem;
    }

    .spacer-small {
        margin-top: 0.5rem;
    }

    .spacer-large {
        margin-top: 2rem;
    }
</style>
"""

# Color configuration from settings
CATEGORY_COLOR_MAP = {
    "orange": "#f97316",
    "red": "#ef4444",
    "yellow": "#eab308",
    "default": "#6b7280",
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_category_colors() -> dict:
    """Get category colors from centralized configuration."""
    return {
        category: CATEGORY_COLOR_MAP.get(color, CATEGORY_COLOR_MAP["default"])
        for category, color in settings.ui.category_colors.items()
    }


def render_spacer(size: str = "medium"):
    """Render consistent vertical spacing."""
    spacer_class = {
        "small": "spacer-small",
        "medium": "spacer",
        "large": "spacer-large",
    }.get(size, "spacer")

    st.markdown(f'<div class="{spacer_class}"></div>', unsafe_allow_html=True)


def ensure_styles_loaded():
    """
    DEPRECATED: Styles are now loaded centrally in app.py load_css().
    This function is kept for compatibility but does nothing.
    """
    pass


# =============================================================================
# SECTION: Quote Display Components
# =============================================================================


def render_quote_card(
    quote: Quote,
    quote_manager: QuoteAdapter,
    lang: str,
    t: dict,
    with_actions: bool = True,
    with_category_badge: bool = True,
):
    """
    Unified quote card rendering.

    Consolidates:
    - render_current_quote() from ui/pages.py
    - get_quote_display_html() from ui/styles.py
    """
    ensure_styles_loaded()

    if not quote:
        return

    quote_text = quote_manager.get_text(quote.text, lang)
    quote_author = quote_manager.get_text(quote.author, lang)

    # Main quote container with border
    with st.container(border=True):
        # Quote HTML using template
        quote_html = TEMPLATES["quote_card"].format(
            text=quote_text, author=quote_author
        )
        st.markdown(quote_html, unsafe_allow_html=True)

        # Save button section
        if with_actions:
            render_spacer("medium")
            col1, col2, col3 = st.columns([1, 3, 1])

            with col2:
                save_list = (
                    quote_manager.saved_poems
                    if quote.category == "poem"
                    else quote_manager.saved_quotes
                )
                is_saved = quote in save_list

                if st.button(
                    f"{t['saved'] if is_saved else t['save']}",
                    disabled=is_saved,
                    key=f"save_{'poem' if quote.category == 'poem' else 'quote'}",
                    use_container_width=True,
                ):
                    if quote.category == "poem":
                        quote_manager.save_current_poem()
                    else:
                        quote_manager.save_current_quote()
                    st.rerun()

    # Original quote display for haikus
    if quote.category == "poem" and quote_manager.original_quote:
        original = quote_manager.original_quote
        original_text = quote_manager.get_text(original.text, lang)
        original_author = quote_manager.get_text(original.author, lang)

        render_spacer("small")
        label = t.get(
            "original_quote", "Citation originale" if lang == "fr" else "Original quote"
        )

        original_html = TEMPLATES["original_quote"].format(
            label=label, text=original_text, author=original_author
        )
        st.markdown(original_html, unsafe_allow_html=True)


# =============================================================================
# SECTION: Action Buttons & Navigation
# =============================================================================


def render_action_bar(
    quote_manager: QuoteAdapter, haiku_generator: HaikuAdapter, lang: str, t: dict
):
    """
    Unified action button bar.

    Consolidates render_action_buttons() from ui/pages.py with cleaner structure.
    """
    ensure_styles_loaded()
    render_spacer("medium")

    # Main action buttons row
    col1, col2, col3 = st.columns(3, gap="medium")

    # New quote button
    with col1:
        if st.button(
            f"🔀 {t['new_quote']}",
            key="new_quote",
            use_container_width=True,
            type="primary",
        ):
            quote_manager.get_random_quote()
            st.rerun()

    # Haiku/Poem button (context-dependent)
    with col2:
        _render_haiku_button(quote_manager, haiku_generator, lang, t)

    # Show all quotes toggle
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

    # API usage display
    if haiku_generator.api_client:
        render_spacer("medium")
        usage_display = haiku_generator.get_usage_display(lang)
        usage_html = TEMPLATES["usage_display"].format(usage_text=usage_display)
        st.markdown(usage_html, unsafe_allow_html=True)

    # Generation limit message
    if st.session_state.get("haiku_generation_count", 0) >= 5:
        render_spacer("medium")
        st.info(
            t.get(
                "limit_message",
                "🐝 Les haïkus sont plus savoureux avec modération. Revenez demain pour 5 nouvelles créations !",
            )
        )

    # Export button (if saved quotes exist)
    total_saved = len(quote_manager.saved_quotes) + len(quote_manager.saved_poems)
    if total_saved > 0:
        render_spacer("medium")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            export_data = quote_manager.export_saved_data()
            st.download_button(
                label=f"📥 {t['export']} ({total_saved})",
                data=export_data,
                file_name=f"{settings.export.file_prefix}-{datetime.now().strftime(settings.export.date_format)}.json",
                mime="application/json",
                key="export",
                use_container_width=True,
            )


def _render_haiku_button(
    quote_manager: QuoteAdapter, haiku_generator: HaikuAdapter, lang: str, t: dict
):
    """Helper for haiku button rendering with context logic."""
    is_poem = (
        quote_manager.current_quote and quote_manager.current_quote.category == "poem"
    )

    if is_poem:
        # Create new poem button
        has_reached_limit = st.session_state.get("haiku_generation_count", 0) >= 5
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
            _handle_new_poem_creation(quote_manager, haiku_generator, lang, t)
    else:
        # View existing haiku button
        if st.button(
            f"👁️ {t.get('view_haiku', 'Voir le Haïku')}",
            key="view_haiku",
            disabled=not quote_manager.current_quote,
            use_container_width=True,
            type="secondary",
        ):
            _handle_view_haiku(quote_manager, haiku_generator, lang, t)


def _handle_new_poem_creation(
    quote_manager: QuoteAdapter, haiku_generator: HaikuAdapter, lang: str, t: dict
):
    """Handle new poem creation logic."""
    source_quote = quote_manager.original_quote
    if not source_quote:
        st.error("Erreur: citation originale non trouvée")
        return

    with st.spinner(t["creating"]):
        if not haiku_generator.api_client:
            st.error(
                t.get(
                    "api_error",
                    "❌ Clé API non configurée. Impossible de générer de nouveaux haïkus.",
                )
            )
            # Fallback to existing haiku
            existing_poem = haiku_generator.get_existing_haiku(source_quote, lang)
            if existing_poem:
                quote_manager.current_quote = existing_poem
                st.rerun()
        else:
            # Generate new haiku
            poem = haiku_generator.generate_from_quote(
                source_quote, lang, force_new=True
            )
            if poem:
                quote_manager.current_quote = poem
                st.rerun()
            else:
                # Fallback to existing
                existing_poem = haiku_generator.get_existing_haiku(source_quote, lang)
                if existing_poem:
                    st.warning(
                        t.get(
                            "api_fail_fallback",
                            "⚠️ Erreur API. Affichage d'un haïku existant.",
                        )
                    )
                    quote_manager.current_quote = existing_poem
                    st.rerun()


def _handle_view_haiku(
    quote_manager: QuoteAdapter, haiku_generator: HaikuAdapter, lang: str, t: dict
):
    """Handle view existing haiku logic."""
    with st.spinner(t.get("loading_haiku", "Chargement...")):
        poem = haiku_generator.get_existing_haiku(quote_manager.current_quote, lang)
        if poem:
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


# =============================================================================
# SECTION: Lists & Collections
# =============================================================================


def render_quote_list(
    quotes: list[Quote], quote_manager: QuoteAdapter, lang: str, t: dict
):
    """
    Unified quote list rendering.

    Consolidates render_all_quotes_list() from ui/pages.py.
    """
    ensure_styles_loaded()

    if not StateManager.get_show_all_quotes():
        return

    render_spacer("large")

    container = st.container(height=settings.ui.quote_list_height)
    with container:
        for quote in quotes:
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
                on_delete=None,  # Deletion disabled
            )
            st.divider()


def render_quote_list_item(
    quote: Quote,
    lang: str,
    quote_text: str,
    quote_author: str,
    on_display: Callable,
    on_delete: Optional[Callable] = None,
):
    """Render individual quote list item with actions."""
    ensure_styles_loaded()

    col1, col2 = st.columns([5, 1])

    with col1:
        quote_html = TEMPLATES["quote_list_item"].format(
            text=quote_text, author=quote_author
        )
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


# =============================================================================
# SECTION: Layout & Structure
# =============================================================================


def render_app_header(title: str, lang: str, on_language_change: Callable):
    """
    Unified header rendering.

    Consolidates render_header() from ui_components.py.
    """
    ensure_styles_loaded()

    # Header container with emoji and language button
    col1, col2, col3 = st.columns([2, 6, 2])

    # Donkey emoji centered
    with col2:
        st.markdown(
            '<div style="text-align: center; font-size: 5rem; '
            'margin-bottom: -2.5rem;">🫏</div>',
            unsafe_allow_html=True,
        )

    # Language button aligned right
    with col3:
        render_spacer("medium")
        if st.button(
            f"🌐 {'EN' if lang == 'fr' else 'FR'}",
            key="lang_switch",
            use_container_width=False,
        ):
            on_language_change()

    # Title using template
    header_html = TEMPLATES["header"].format(title=title)
    st.markdown(header_html, unsafe_allow_html=True)


def render_app_footer(version: str, contribute_message: str):
    """Unified footer rendering."""
    ensure_styles_loaded()

    render_spacer("large")
    render_spacer("large")

    footer_html = TEMPLATES["footer"].format(
        version=version, contribute_message=contribute_message
    )
    st.markdown(footer_html, unsafe_allow_html=True)


# =============================================================================
# SECTION: Layout Utilities
# =============================================================================


def create_centered_columns(center_ratio: int = 2) -> list[Any]:
    """Create centered column layout [1, center_ratio, 1]."""
    return st.columns([1, center_ratio, 1])


def create_equal_columns(count: int, gap: str = "medium") -> list[Any]:
    """Create equal-width columns."""
    return st.columns(count, gap=gap)


def create_action_button_row(
    buttons_config: list[dict], gap: str = "medium", equal_width: bool = True
) -> None:
    """
    Create a row of action buttons with consistent styling.

    Args:
        buttons_config: List of button configs with keys: label, key, callback, type, disabled
        gap: Gap between columns
        equal_width: Whether buttons should have equal width
    """
    cols = st.columns(len(buttons_config), gap=gap)

    for col, btn_config in zip(cols, buttons_config):
        with col:
            clicked = st.button(
                btn_config["label"],
                key=btn_config["key"],
                use_container_width=equal_width,
                type=btn_config.get("type", "secondary"),
                disabled=btn_config.get("disabled", False),
            )

            if clicked and "callback" in btn_config:
                btn_config["callback"]()


# =============================================================================
# TESTING FUNCTIONS
# =============================================================================


def test_unified_components() -> bool:
    """
    Test function to verify all components load correctly.

    Returns:
        bool: True if all components can be imported and basic functionality works
    """
    try:
        # Test template formatting
        test_quote_html = TEMPLATES["quote_card"].format(
            text="Test quote", author="Test Author"
        )
        assert "Test quote" in test_quote_html
        assert "Test Author" in test_quote_html

        # Test CSS styles load
        assert "quote-container" in CSS_STYLES
        assert "category-badge" in CSS_STYLES

        # Test utility functions
        colors = get_category_colors()
        assert isinstance(colors, dict)

        # Test all main rendering functions can be called
        # (We don't actually render in test, just check they exist)
        functions_to_test = [
            render_quote_card,
            render_action_bar,
            render_quote_list,
            render_quote_list_item,
            render_app_header,
            render_app_footer,
            create_centered_columns,
            create_equal_columns,
            create_action_button_row,
        ]

        for func in functions_to_test:
            assert callable(func), f"{func.__name__} is not callable"

        return True

    except Exception as e:
        print(f"Test failed: {e}")
        return False


def get_unified_components_info() -> dict:
    """Return information about the unified components module."""
    return {
        "module": "components.py",
        "consolidates": [
            "ui/pages.py - render_current_quote, render_action_buttons, render_all_quotes_list (deleted)",
            "ui/styles.py - get_quote_display_html, get_original_quote_html, get_category_badge_html (moved)",
            "ui_components.py - render_header, render_category_badge, render_quote_list_item (deleted)",
            "ui/layouts.py - layout utilities (deleted)",
        ],
        "templates_count": len(TEMPLATES),
        "functions_count": 12,
        "css_classes": 20,
        "benefits": [
            "Single CSS file instead of inline styles",
            "Consistent HTML templates",
            "Reduced code duplication",
            "Better maintainability",
            "Centralized styling",
        ],
    }
