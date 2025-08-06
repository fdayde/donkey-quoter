"""
Service métier pour la gestion des citations (logique pure, sans UI).
"""

import json
import random
from datetime import datetime
from typing import Optional

from .models import Quote, QuoteInput


class QuoteService:
    """Service métier pour la gestion des citations sans dépendances UI."""

    def get_text(self, text_dict: dict[str, str], language: str) -> str:
        """Obtient le texte dans la langue spécifiée."""
        if isinstance(text_dict, dict):
            return text_dict.get(language, text_dict.get("fr", ""))
        return str(text_dict)

    def get_random_quote(self, quotes: list[Quote]) -> Optional[Quote]:
        """Retourne une citation aléatoire."""
        if quotes:
            return random.choice(quotes)
        return None

    def filter_by_category(self, quotes: list[Quote], category: str) -> list[Quote]:
        """Filtre les citations par catégorie."""
        if category == "all":
            return quotes
        return [q for q in quotes if q.category == category]

    def filter_by_type(self, quotes: list[Quote], quote_type: str) -> list[Quote]:
        """Filtre les citations par type."""
        if quote_type == "all":
            return quotes
        return [q for q in quotes if q.type == quote_type]

    def create_quote_from_input(self, quote_input: QuoteInput, language: str) -> Quote:
        """Crée un objet Quote à partir d'un QuoteInput."""
        return Quote(
            id=f"user_{int(datetime.now().timestamp())}",
            text={
                language: quote_input.text,
                "fr" if language == "en" else "en": quote_input.text,
            },
            author={
                language: quote_input.author,
                "fr" if language == "en" else "en": quote_input.author,
            },
            category=quote_input.category,
            type="user",
        )

    def update_quote_from_input(
        self, quote: Quote, quote_input: QuoteInput, language: str
    ) -> Quote:
        """Met à jour un objet Quote avec les nouvelles données."""
        updated_quote = quote.model_copy()
        updated_quote.text[language] = quote_input.text
        updated_quote.text["fr" if language == "en" else "en"] = quote_input.text
        updated_quote.author[language] = quote_input.author
        updated_quote.author["fr" if language == "en" else "en"] = quote_input.author
        updated_quote.category = quote_input.category
        return updated_quote

    def find_quote_by_id(self, quotes: list[Quote], quote_id: str) -> Optional[Quote]:
        """Trouve une citation par son ID."""
        for quote in quotes:
            if quote.id == quote_id:
                return quote
        return None

    def remove_quote_by_id(self, quotes: list[Quote], quote_id: str) -> list[Quote]:
        """Supprime une citation par son ID."""
        return [q for q in quotes if q.id != quote_id]

    def add_quote_to_list(self, quotes: list[Quote], quote: Quote) -> list[Quote]:
        """Ajoute une citation en tête de liste."""
        new_quotes = quotes.copy()
        new_quotes.insert(0, quote)
        return new_quotes

    def is_quote_in_list(self, quotes: list[Quote], quote: Quote) -> bool:
        """Vérifie si une citation est dans la liste."""
        return quote in quotes

    def add_quote_if_not_exists(
        self, quotes: list[Quote], quote: Quote
    ) -> tuple[list[Quote], bool]:
        """Ajoute une citation si elle n'existe pas déjà."""
        if self.is_quote_in_list(quotes, quote):
            return quotes, False
        new_quotes = quotes.copy()
        new_quotes.append(quote)
        return new_quotes, True

    def export_quotes_to_json(
        self, saved_quotes: list[Quote], saved_poems: list[Quote]
    ) -> str:
        """Exporte les citations sauvegardées au format JSON."""
        data = {
            "savedQuotes": [q.model_dump() for q in saved_quotes],
            "savedPoems": [p.model_dump() for p in saved_poems],
            "exportDate": datetime.now().isoformat(),
            "totalSavedQuotes": len(saved_quotes),
            "totalSavedPoems": len(saved_poems),
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
