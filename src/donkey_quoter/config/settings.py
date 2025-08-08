"""
Configuration unifiée de l'application Donkey Quoter.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppSettings:
    """Configuration générale de l'application."""

    page_title: str = "Donkey Quoter"
    page_icon: str = "🫏"
    layout: str = "centered"
    initial_sidebar_state: str = "collapsed"


@dataclass
class PathSettings:
    """Configuration des chemins de fichiers."""

    base_dir: Path = Path(__file__).parent.parent
    styles_css_path: Path = base_dir / "styles.css"


@dataclass
class UISettings:
    """Configuration de l'interface utilisateur."""

    category_colors: dict[str, str] = None
    quote_list_height: int = 400
    progress_bar_delay: float = 0.015  # secondes

    def __post_init__(self):
        if self.category_colors is None:
            self.category_colors = {
                "classic": "orange",
                "personal": "orange",
                "poem": "red",
                "humor": "yellow",
            }


@dataclass
class ExportSettings:
    """Configuration de l'export."""

    date_format: str = "%Y%m%d"
    file_prefix: str = "donkey-quoter"


@dataclass
class TokenSettings:
    """Configuration de l'estimation des tokens."""

    chars_per_token: int = 4  # Approximation : 4 caractères = 1 token
    haiku_output_tokens: int = 150  # Estimation tokens pour un haïku généré
    prompt_overhead_tokens: int = 50  # Tokens supplémentaires du prompt système


@dataclass
class PricingSettings:
    """Configuration des prix des API Claude."""

    claude_pricing: dict[str, dict[str, float]] = None

    def __post_init__(self):
        if self.claude_pricing is None:
            # Prix en USD par million de tokens
            self.claude_pricing = {
                "claude-3-5-haiku-20241022": {
                    "input": 0.80,  # $0.80 per million input tokens
                    "output": 4,  # $4 per million output tokens
                },
                "claude-3-haiku-20240307": {
                    "input": 0.25,  # $0.25 per million input tokens
                    "output": 1.25,  # $1.25 per million output tokens
                },
            }


@dataclass
class ModelSettings:
    """Configuration du mapping des modèles."""

    model_to_author: dict[str, dict[str, str]] = None

    def __post_init__(self):
        if self.model_to_author is None:
            self.model_to_author = {
                "claude-3-5-haiku-20241022": {
                    "fr": "Claude Haiku 3.5",
                    "en": "Claude Haiku 3.5",
                },
                "claude-3-haiku-20240307": {
                    "fr": "Claude Haiku 3",
                    "en": "Claude Haiku 3",
                },
                "unknown": {
                    "fr": "Maître du Haïku",
                    "en": "Haiku Master",
                },
                "default": {
                    "fr": "Claude Haiku",
                    "en": "Claude Haiku",
                },
            }

    def get_author_for_model(self, model: str, language: str = "fr") -> str:
        """
        Retourne le nom d'auteur approprié pour un modèle donné.

        Args:
            model: Le nom du modèle utilisé
            language: La langue (fr ou en)

        Returns:
            Le nom d'auteur à afficher
        """
        if model in self.model_to_author:
            return self.model_to_author[model][language]

        # Si le modèle contient "haiku", utiliser un nom générique
        if "haiku" in model.lower():
            return self.model_to_author["default"][language]

        # Sinon, utiliser le nom par défaut
        return self.model_to_author["unknown"][language]


@dataclass
class Settings:
    """Configuration principale de l'application."""

    def __post_init__(self):
        self.app = AppSettings()
        self.paths = PathSettings()
        self.ui = UISettings()
        self.export = ExportSettings()
        self.tokens = TokenSettings()
        self.pricing = PricingSettings()
        self.models = ModelSettings()


# Instance globale des paramètres
settings = Settings()


# Compatibilité avec l'ancien système (à supprimer progressivement)
PAGE_CONFIG = {
    "page_title": settings.app.page_title,
    "page_icon": settings.app.page_icon,
    "layout": settings.app.layout,
    "initial_sidebar_state": settings.app.initial_sidebar_state,
}

BASE_DIR = settings.paths.base_dir
STYLES_CSS_PATH = settings.paths.styles_css_path
CATEGORY_COLORS = settings.ui.category_colors
QUOTE_LIST_HEIGHT = settings.ui.quote_list_height
PROGRESS_BAR_DELAY = settings.ui.progress_bar_delay
EXPORT_DATE_FORMAT = settings.export.date_format
EXPORT_FILE_PREFIX = settings.export.file_prefix
CLAUDE_PRICING = settings.pricing.claude_pricing
TOKEN_ESTIMATION = {
    "chars_per_token": settings.tokens.chars_per_token,
    "haiku_output_tokens": settings.tokens.haiku_output_tokens,
    "prompt_overhead_tokens": settings.tokens.prompt_overhead_tokens,
}
MODEL_TO_AUTHOR = settings.models.model_to_author


def get_author_for_model(model: str, language: str = "fr") -> str:
    """Fonction de compatibilité pour get_author_for_model."""
    return settings.models.get_author_for_model(model, language)
