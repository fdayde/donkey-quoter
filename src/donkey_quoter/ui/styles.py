"""
Utilitaires pour les styles de l'application.

Ce module contient la logique métier pour les couleurs et styles.
Les couleurs principales sont définies dans .streamlit/config.toml.
Les couleurs étendues sont définies ici pour les besoins spécifiques.
"""

from ..config.settings import settings

# Palette de couleurs étendue - Cohérente avec la palette chaleureuse 2025
# Ces couleurs complètent les couleurs principales définies dans .streamlit/config.toml
EXTENDED_COLORS = {
    # Couleurs chaudes harmonieuses
    "warm_orange": "#ea580c",  # Orange-600 - accents vibrants
    "warm_brown": "#a16207",  # Amber-700 - texte secondaire
    "warm_dark": "#78350f",  # Amber-900 - texte foncé
    "warm_cream": "#fef3c7",  # Amber-100 - backgrounds doux
}

# Mapping des couleurs de catégories - palette cohérente
CATEGORY_COLOR_MAP = {
    "orange": EXTENDED_COLORS["warm_orange"],
    "red": "#dc2626",  # Red-600 moderne
    "yellow": "#d97706",  # Amber-600 harmonieux
    "default": EXTENDED_COLORS["warm_dark"],
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
        color_key: Clé de couleur ("warm_orange", "warm_brown", etc.)

    Returns:
        Code couleur hexadécimal
    """
    return EXTENDED_COLORS.get(color_key, EXTENDED_COLORS["warm_brown"])


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
