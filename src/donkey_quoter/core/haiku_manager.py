"""
Gestionnaire centralisé pour les opérations haiku.
Suit les principes DRY, KISS, YAGNI.
"""

from typing import Any, Optional

from ..config.settings import CLAUDE_PRICING, TOKEN_ESTIMATION
from ..data import CLASSIC_QUOTES
from ..infrastructure.anthropic_client import AnthropicClient
from .models import Quote
from .storage import DataStorage


class HaikuManager:
    """Gestionnaire centralisé pour toutes les opérations haiku."""

    def __init__(self, api_client: Optional[AnthropicClient] = None):
        """Initialise le manager."""
        self.storage = DataStorage()
        self.api_client = api_client
        self.model = api_client.model if api_client else None

    def get_quotes_for_batch(self, regenerate_all: bool = False) -> list[Quote]:
        """Récupère les citations pour génération batch."""
        quotes = []
        for quote_data in CLASSIC_QUOTES:
            quote = Quote(**quote_data)
            if regenerate_all:
                quotes.append(quote)
            else:
                existing = self.storage.haikus_data.get(quote.id, {})
                if not (existing.get("fr") and existing.get("en")):
                    quotes.append(quote)
        return quotes

    def generate_batch(self, quotes: list[Quote]) -> dict[str, dict[str, str]]:
        """Génère des haïkus en batch bilingue."""
        if not self.api_client:
            return {
                q.id: {"fr": f"[DRY] FR {q.id}", "en": f"[DRY] EN {q.id}"}
                for q in quotes
            }

        prompt = self._create_batch_prompt(quotes)
        max_tokens = TOKEN_ESTIMATION["haiku_output_tokens"] * 2 * len(quotes)

        response_text = self.api_client.call_claude(
            prompt, max_tokens=max_tokens, temperature=0.7, model=self.model
        )

        return self._parse_batch_response(response_text)

    def get_statistics(self) -> dict[str, Any]:
        """Calcule les statistiques des haïkus."""
        quotes = [Quote(**q) for q in CLASSIC_QUOTES]

        stats = {"total_quotes": len(quotes), "languages": {}}

        for lang in ["fr", "en"]:
            with_haiku = sum(1 for q in quotes if self.storage.has_haiku(q.id, lang))
            stats["languages"][lang] = {
                "with_haiku": with_haiku,
                "without_haiku": len(quotes) - with_haiku,
                "percentage": (with_haiku / len(quotes)) * 100,
            }

        # Stats bilingues
        both_langs = sum(
            1
            for q in quotes
            if self.storage.has_haiku(q.id, "fr") and self.storage.has_haiku(q.id, "en")
        )
        stats["bilingual"] = {
            "complete": both_langs,
            "percentage": (both_langs / len(quotes)) * 100,
        }

        # Modèles utilisés
        models_used = set()
        for haiku_data in self.storage.haikus_data.values():
            for lang_data in haiku_data.values():
                if isinstance(lang_data, dict) and "model" in lang_data:
                    models_used.add(lang_data["model"])
        stats["models_used"] = sorted(models_used)

        return stats

    def export_data(self, format_type: str = "json") -> dict[str, Any]:
        """Exporte les données selon le format."""
        quotes = [Quote(**q) for q in CLASSIC_QUOTES]

        if format_type == "json":
            export_data = {}
            for quote in quotes:
                quote_data = {
                    "quote": {
                        "id": quote.id,
                        "text": quote.text,
                        "author": quote.author,
                        "category": quote.category,
                    },
                    "haikus": {},
                }

                for lang in ["fr", "en"]:
                    if self.storage.has_haiku(quote.id, lang):
                        haiku_info = self.storage.get_haiku(quote.id, lang)
                        quote_data["haikus"][lang] = (
                            haiku_info
                            if isinstance(haiku_info, dict)
                            else {"text": haiku_info}
                        )

                export_data[quote.id] = quote_data
            return export_data

        elif format_type == "csv":
            rows = []
            for quote in quotes:
                haiku_fr = self.storage.get_haiku(quote.id, "fr")
                haiku_en = self.storage.get_haiku(quote.id, "en")

                if isinstance(haiku_fr, dict):
                    haiku_fr = haiku_fr.get("text", "")
                if isinstance(haiku_en, dict):
                    haiku_en = haiku_en.get("text", "")

                rows.append(
                    [
                        quote.id,
                        quote.category,
                        quote.text["fr"],
                        quote.author["fr"],
                        quote.text["en"],
                        quote.author["en"],
                        haiku_fr or "",
                        haiku_en or "",
                    ]
                )
            return {
                "headers": [
                    "quote_id",
                    "category",
                    "quote_fr",
                    "author_fr",
                    "quote_en",
                    "author_en",
                    "haiku_fr",
                    "haiku_en",
                ],
                "rows": rows,
            }

    def calculate_cost_estimate(
        self, num_quotes: int, batch_size: int = 5
    ) -> dict[str, Any]:
        """Calcule une estimation de coût avec info sur la méthode."""
        if not self.model or self.model not in CLAUDE_PRICING:
            return {"cost": 0.0, "method": "no_model", "status": "unavailable"}

        pricing = CLAUDE_PRICING[self.model]
        batches = (num_quotes + batch_size - 1) // batch_size

        # Essayer count_tokens pour le premier batch si API disponible
        if self.api_client and batches > 0:
            # Créer un échantillon pour estimation précise
            sample_quotes = [
                Quote(**q) for q in CLASSIC_QUOTES[: min(batch_size, num_quotes)]
            ]
            sample_prompt = self._create_batch_prompt(sample_quotes)
            messages = [{"role": "user", "content": sample_prompt}]

            precise_tokens, status = self.api_client.count_tokens_safe(messages)
            if precise_tokens is not None:
                # Estimation précise basée sur count_tokens
                output_tokens_per_batch = (
                    TOKEN_ESTIMATION["haiku_output_tokens"] * 2 * len(sample_quotes)
                )
                total_input_tokens = precise_tokens * batches
                total_output_tokens = output_tokens_per_batch * batches

                cost = (total_input_tokens / 1_000_000) * pricing["input"] + (
                    total_output_tokens / 1_000_000
                ) * pricing["output"]

                return {
                    "cost": cost,
                    "method": "count_tokens",
                    "status": "precise",
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                }

        # Fallback vers estimation basique
        tokens_per_batch = 200 + (
            TOKEN_ESTIMATION["haiku_output_tokens"] * 2 * batch_size
        )
        total_tokens = tokens_per_batch * batches
        cost = (total_tokens / 1_000_000) * pricing["output"]

        return {
            "cost": cost,
            "method": "estimation",
            "status": "basic",
            "total_tokens": total_tokens,
        }

    def _create_batch_prompt(self, quotes: list[Quote]) -> str:
        """Crée un prompt pour génération batch."""
        prompt = (
            "Génère des haïkus poétiques en français ET en anglais "
            "pour chaque citation.\n\n"
            "Format JSON :\n"
            "{\n"
            '  "quote_id": {"fr": "haiku fr", "en": "haiku en"}\n'
            "}\n\n"
            "Citations :\n"
        )

        for quote in quotes:
            prompt += f"\nID: {quote.id}\n"
            prompt += f'FR: "{quote.text["fr"]}" - {quote.author["fr"]}\n'
            prompt += f'EN: "{quote.text["en"]}" - {quote.author["en"]}\n'

        return prompt

    def _parse_batch_response(self, response: str) -> dict[str, dict[str, str]]:
        """Parse la réponse JSON."""
        try:
            import json
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            return json.loads(json_match.group()) if json_match else {}
        except Exception:
            return {}
