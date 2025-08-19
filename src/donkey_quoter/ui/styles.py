"""
Utilitaires pour les styles de l'application.

Ce module contient la logique métier pour les couleurs et styles.
Les couleurs principales sont définies dans .streamlit/config.toml.
Les couleurs étendues sont définies ici pour les besoins spécifiques.
"""

from ..config.settings import settings

# Palette de couleurs étendue - Complémentaire au theme Streamlit
# Ces couleurs ne sont pas supportées nativement par Streamlit
EXTENDED_COLORS = {
    # Seulement les couleurs réellement utilisées dans l'application
    "amber_50": "#fffbeb",  # scrollbar background
    "amber_700": "#b45309",  # texte auteur, stats number
    "amber_800": "#92400e",  # original quote label
    "orange_600": "#ea580c",  # catégorie orange
    "yellow_700": "#a16207",  # catégorie yellow
}

# Mapping des couleurs de catégories
CATEGORY_COLOR_MAP = {
    "orange": EXTENDED_COLORS["orange_600"],
    "red": "#ef4444",
    "yellow": EXTENDED_COLORS["yellow_700"],
    "default": "#6b7280",
}


def get_category_colors() -> dict:
    """Récupère les couleurs de catégories depuis la configuration centralisée."""
    return {
        category: CATEGORY_COLOR_MAP.get(color, CATEGORY_COLOR_MAP["default"])
        for category, color in settings.ui.category_colors.items()
    }


def get_extended_color(color_key: str) -> str:
    """
    Retourne une couleur de la palette étendue.

    Args:
        color_key: Clé de couleur ("amber_50", "rose_500", etc.)

    Returns:
        Code couleur hexadécimal
    """
    return EXTENDED_COLORS.get(color_key, EXTENDED_COLORS["amber_700"])


def get_streamlit_theme_color(color_type: str) -> str:
    """
    Retourne le nom de variable CSS Streamlit pour les couleurs du thème.

    Args:
        color_type: Type de couleur ("primary", "secondary", "background", "text")

    Returns:
        Nom de la variable CSS Streamlit
    """
    color_mapping = {
        "primary": "var(--primary-color)",
        "secondary": "var(--secondary-background-color)",
        "background": "var(--background-color)",
        "text": "var(--text-color)",
    }
    return color_mapping.get(color_type, "var(--primary-color)")
