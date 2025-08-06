"""
Templates de prompts pour la génération de haïkus.
"""

# Templates de prompts par langue
HAIKU_PROMPT_TEMPLATES: dict[str, str] = {
    "fr": """Génère un haïku en français inspiré de cette citation :
"{quote_text}" - {quote_author}

Le haïku doit :
- Respecter le format 5-7-5 syllabes
- Capturer l'essence de la citation
- Utiliser une imagerie poétique avec un âne/baudet/bourrique
- Être contemplatif et philosophique

Réponds uniquement avec le haïku (3 lignes), sans explication.""",
    "en": """Generate an English haiku inspired by this quote:
"{quote_text}" - {quote_author}

The haiku must:
- Follow the 5-7-5 syllable format
- Capture the essence of the quote
- Use poetic imagery with a donkey/mule/ass
- Be contemplative and philosophical

Reply only with the haiku (3 lines), no explanation.""",
}


def build_haiku_prompt(quote_text: str, quote_author: str, language: str = "fr") -> str:
    """
    Construit un prompt pour la génération de haïku.

    Args:
        quote_text: Le texte de la citation
        quote_author: L'auteur de la citation
        language: La langue du haïku ('fr' ou 'en')

    Returns:
        Le prompt formaté
    """
    template = HAIKU_PROMPT_TEMPLATES.get(language, HAIKU_PROMPT_TEMPLATES["fr"])
    return template.format(quote_text=quote_text, quote_author=quote_author)
