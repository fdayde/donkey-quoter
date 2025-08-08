"""
Constantes et utilitaires pour les styles CSS de l'application.
"""

from ..config.settings import settings

# Palette de couleurs principale
COLORS = {
    "primary": "#d97706",  # Orange principal
    "primary_dark": "#78350f",  # Orange foncé pour le texte
    "primary_light": "#fef3c7",  # Orange très clair pour les fonds
    "secondary": "#b45309",  # Orange moyen pour les auteurs
    "accent": "#92400e",  # Orange accent pour les détails
    "background_light": "rgba(254, 243, 199, 0.3)",  # Fond léger
    "background_border": "rgba(254, 243, 199, 0.5)",  # Bordure
}

# Familles de polices
FONTS = {
    "main": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
}

# Mapper les couleurs textuelles vers les codes hexadécimaux
CATEGORY_COLOR_MAP = {
    "orange": "#f97316",
    "red": "#ef4444",
    "yellow": "#eab308",
    "default": "#6b7280",
}


def get_category_colors() -> dict:
    """Récupère les couleurs de catégories depuis la configuration centralisée."""
    return {
        category: CATEGORY_COLOR_MAP.get(color, CATEGORY_COLOR_MAP["default"])
        for category, color in settings.ui.category_colors.items()
    }


def get_quote_container_style() -> str:
    """Retourne les styles CSS pour le conteneur de citation."""
    return f"""
    <style>
    .quote-container {{
        padding: 2rem;
        text-align: center;
    }}

    .quote-opening {{
        font-size: 4rem;
        color: {COLORS["primary"]};
        font-family: {FONTS["main"]};
        line-height: 0.5;
        margin-bottom: -1.5rem;
    }}

    .quote-text {{
        font-size: 1.25rem;
        color: {COLORS["primary_dark"]};
        line-height: 1.8;
        font-weight: 300;
        font-family: {FONTS["main"]};
        text-align: center;
        margin: 0 2rem;
        white-space: pre-line;
    }}

    .quote-author {{
        text-align: right;
        margin-right: 2rem;
        margin-top: 1rem;
        color: {COLORS["secondary"]};
        font-size: 0.75rem;
        font-weight: 500;
        font-family: {FONTS["main"]};
    }}
    </style>
    """


def get_header_style(title: str, subtitle: str) -> str:
    """Retourne le HTML stylisé pour l'en-tête."""
    return f"""
    <div style="text-align: center;">
        <h1 style="font-family: {FONTS["main"]};
            font-size: 2.5rem; font-weight: 300; color: {COLORS["primary_dark"]};
            margin: 0;">{title}</h1>
        <p style="font-family: {FONTS["main"]};
            color: {COLORS["primary"]}; font-size: 1.125rem; font-weight: 300;
            margin-top: 0.25rem; margin-bottom: 2rem;">{subtitle}</p>
    </div>
    """


def get_quote_display_html(quote_text: str, quote_author: str) -> str:
    """Retourne le HTML stylisé pour l'affichage d'une citation."""
    return f"""
    <div style="padding: 2rem;">
        <div style="text-align: center; margin-bottom: -1.5rem;">
            <span style="font-size: 4rem; color: {COLORS["primary"]};
                font-family: {FONTS["main"]};
                line-height: 0.5;">"</span>
        </div>
        <div style="font-size: 1.25rem; color: {COLORS["primary_dark"]}; line-height: 1.8;
            font-weight: 300; font-family: {FONTS["main"]};
            text-align: center; margin: 0 2rem; white-space: pre-line;">
            {quote_text}
        </div>
        <div style="text-align: right; margin-right: 2rem; margin-top: 1rem;">
            <span style="color: {COLORS["secondary"]}; font-size: 0.75rem;
                font-weight: 500; font-family: {FONTS["main"]};">— {quote_author}</span>
        </div>
    </div>
    """


def get_original_quote_html(
    original_text: str, original_author: str, label: str
) -> str:
    """Retourne le HTML stylisé pour la citation originale."""
    return f"""
    <div style="text-align: center; padding: 0.5rem;
        background-color: {COLORS["background_light"]};
        border-radius: 0.5rem; margin-top: 0.5rem;">
        <p style="font-size: 0.75rem; color: {COLORS["accent"]};
            font-style: italic; margin: 0;">
            {label} :
        </p>
        <p style="font-size: 0.75rem; color: {COLORS["primary_dark"]};
            margin: 0.25rem 0 0 0;">
            "{original_text}" — {original_author}
        </p>
    </div>
    """


def get_category_badge_html(category_label: str, category: str) -> str:
    """Retourne le HTML stylisé pour un badge de catégorie."""
    category_colors = get_category_colors()
    color = category_colors.get(category, CATEGORY_COLOR_MAP["default"])

    return f"""
    <span style="display: inline-block; padding: 0.25rem 0.75rem;
        background-color: {color}; color: white; border-radius: 1rem;
        font-size: 0.75rem; font-weight: 500; margin-bottom: 0.5rem;">
        {category_label}
    </span>
    """


def get_quote_list_item_html(quote_text: str, quote_author: str) -> str:
    """Retourne le HTML stylisé pour un élément de liste de citations."""
    return f"""
    <p style="font-family: {FONTS["main"]};
        font-weight: 300; margin: 0.5rem 0; color: {COLORS["primary_dark"]};
        font-size: 0.875rem;">
        "{quote_text}"
    </p>
    <p style="font-family: {FONTS["main"]};
        font-weight: 500; margin: 0; color: rgba(180, 83, 9, 0.7);
        font-size: 0.75rem;">— {quote_author}
    </p>
    """


def get_usage_display_html(usage_text: str) -> str:
    """Retourne le HTML stylisé pour l'affichage du compteur d'usage."""
    return f"""
    <div style="text-align: center; color: {COLORS["accent"]};
        font-size: 0.875rem;">{usage_text}</div>
    """


def get_footer_html(version: str, contribute_message: str) -> str:
    """Retourne le HTML stylisé pour le footer."""
    return f"""
    <div style="text-align: center; padding: 2rem 0 1rem 0;
        border-top: 1px solid {COLORS["background_border"]}; margin-top: 3rem;">
        <a href="https://github.com/fdayde/donkey-quoter" target="_blank"
            style="color: {COLORS["primary"]}; text-decoration: none; font-size: 0.875rem;">
            <svg width="20" height="20" viewBox="0 0 24 24"
                 fill="currentColor" style="vertical-align: middle;
                 margin-right: 0.5rem;">
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
        <p style="font-size: 0.625rem; font-style: italic; color: {COLORS["primary"]};
            margin-top: 0.5rem; margin-bottom: 0;">
            ↑ {contribute_message}
        </p>
        <p style="font-size: 0.625rem; color: #a3a3a3; margin-top: 0.75rem; margin-bottom: 0;">
            Donkey Quoter v{version}
        </p>
    </div>
    """
