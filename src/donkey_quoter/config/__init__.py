"""Package de configuration."""

from pathlib import Path

# Configuration de la page
PAGE_CONFIG = {
    "page_title": "Donkey Quoter",
    "page_icon": "🫏",
    "layout": "centered",
    "initial_sidebar_state": "collapsed",
}

# Chemins des fichiers
BASE_DIR = Path(__file__).parent.parent
STYLES_CSS_PATH = BASE_DIR / "styles.css"

# Couleurs par catégorie
CATEGORY_COLORS = {
    "classic": "orange",
    "personal": "orange",
    "poem": "red",
    "humor": "yellow",
}

# Configuration de l'export
EXPORT_DATE_FORMAT = "%Y%m%d"
EXPORT_FILE_PREFIX = "donkey-quoter"

# Dimensions et styles
QUOTE_LIST_HEIGHT = 400
PROGRESS_BAR_DELAY = 0.015  # secondes
