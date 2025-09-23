"""
Package de configuration - DEPRECATED.

Ce module est conservé pour la compatibilité mais toute la configuration
a été migrée vers settings.py. Utilisez settings.py pour toute nouvelle configuration.
"""

from .settings import (
    CATEGORY_COLORS,
    CLAUDE_PRICING,
    EXPORT_DATE_FORMAT,
    EXPORT_FILE_PREFIX,
    PAGE_CONFIG,
    PROGRESS_BAR_DELAY,
    QUOTE_LIST_HEIGHT,
    STYLES_CSS_PATH,
    TOKEN_ESTIMATION,
    get_author_for_model,
    settings,
)

__all__ = [
    "PAGE_CONFIG",
    "STYLES_CSS_PATH",
    "CATEGORY_COLORS",
    "EXPORT_DATE_FORMAT",
    "EXPORT_FILE_PREFIX",
    "QUOTE_LIST_HEIGHT",
    "PROGRESS_BAR_DELAY",
    "CLAUDE_PRICING",
    "TOKEN_ESTIMATION",
    "get_author_for_model",
    "settings",
]
