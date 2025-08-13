"""
Constantes CSS pour les styles de l'application.

Ce module contient uniquement les constantes de couleurs et polices
utilisées par les composants UI unifiés.
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
