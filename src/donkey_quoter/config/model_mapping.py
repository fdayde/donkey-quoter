"""
Configuration du mapping entre modèles Claude et noms d'auteurs.
"""

# Mapping des modèles vers les noms d'auteurs affichés
MODEL_TO_AUTHOR = {
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


def get_author_for_model(model: str, language: str = "fr") -> str:
    """
    Retourne le nom d'auteur approprié pour un modèle donné.

    Args:
        model: Le nom du modèle utilisé
        language: La langue (fr ou en)

    Returns:
        Le nom d'auteur à afficher
    """
    if model in MODEL_TO_AUTHOR:
        return MODEL_TO_AUTHOR[model][language]

    # Si le modèle contient "haiku", utiliser un nom générique
    if "haiku" in model.lower():
        return MODEL_TO_AUTHOR["default"][language]

    # Sinon, utiliser le nom par défaut
    return MODEL_TO_AUTHOR["unknown"][language]
