"""
Service métier pour la génération de haïkus (logique pure, sans UI).
"""

import os
from datetime import datetime
from typing import Optional

from ..config.settings import settings
from ..prompts.haiku_prompts import build_haiku_prompt
from .models import Quote


class HaikuService:
    """Service métier pour la génération de haïkus sans dépendances UI."""

    def __init__(self, api_client=None, storage=None):
        """
        Initialise le service de haïkus.

        Args:
            api_client: Client API pour la génération
            storage: Instance de DataStorage pour le stockage des haïkus
        """
        self.api_client = api_client
        self.storage = storage

    def can_generate_new_haiku(self, generation_count: int) -> bool:
        """
        Vérifie si on peut générer un nouveau haïku.

        Args:
            generation_count: Nombre de haïkus déjà générés

        Returns:
            True si on peut générer un nouveau haïku
        """
        return self.api_client is not None and generation_count < 5

    def generate_via_api(
        self, quote_text: str, quote_author: str, language: str
    ) -> Optional[str]:
        """
        Génère un haïku via l'API Claude.

        Args:
            quote_text: Texte de la citation
            quote_author: Auteur de la citation
            language: Langue du haïku

        Returns:
            Le haïku généré ou None en cas d'erreur
        """
        if not self.api_client:
            return None

        try:
            # Construire le prompt avec le module dédié
            prompt = build_haiku_prompt(quote_text, quote_author, language)

            # Limiter la longueur du prompt si nécessaire
            max_chars = getattr(self.api_client, "max_tokens_input", 200) * 4
            if len(prompt) > max_chars:
                prompt = prompt[:max_chars]

            # Appel générique à l'API
            haiku_raw = self.api_client.call_claude(prompt)

            # Vérifier et formater le haïku
            return self._format_haiku(haiku_raw)

        except Exception:
            return None

    def _format_haiku(self, haiku_text: str) -> str:
        """
        Formate et valide un haïku généré.

        Args:
            haiku_text: Texte brut du haïku

        Returns:
            Haïku formaté
        """
        haiku = haiku_text.strip()

        # Vérifier que c'est bien un haïku (3 lignes)
        lines = haiku.split("\n")
        if len(lines) == 3:
            return haiku
        else:
            # Essayer de reformater si nécessaire
            words = haiku.split()
            if len(words) >= 10:
                # Approximation pour découper en 3 lignes
                third = len(words) // 3
                return "\n".join(
                    [
                        " ".join(words[:third]),
                        " ".join(words[third : 2 * third]),
                        " ".join(words[2 * third :]),
                    ]
                )
            return haiku

    def get_stored_haiku(self, quote_id: str, language: str) -> Optional[str]:
        """
        Récupère un haïku stocké.

        Args:
            quote_id: ID de la citation
            language: Langue du haïku

        Returns:
            Le haïku stocké ou None
        """
        if not self.storage:
            return None
        return self.storage.get_haiku(quote_id, language)

    def get_fallback_haiku(self, language: str) -> str:
        """
        Retourne un haïku de fallback.

        Args:
            language: Langue du haïku

        Returns:
            Un haïku de fallback
        """
        fallbacks = {
            "fr": [
                "Âne philosophe\nMédite sous le vieux chêne\nSagesse simple",
                "Baudet tranquille\nPorte le poids de la vie\nPas après pas",
                "Oreilles dressées\nÉcoutent le vent qui passe\nMoment présent",
            ],
            "en": [
                "Donkey philosopher\nMeditates under old oak\nSimple wisdom flows",
                "Peaceful mule carries\nLife's burden step by step\nQuiet strength endures",
                "Ears raised high, listening\nTo the passing wind's whisper\nPresent moment speaks",
            ],
        }

        import random

        return random.choice(fallbacks.get(language, fallbacks["fr"]))

    def create_haiku_quote(
        self,
        haiku_text: str,
        language: str,
        model: str = "unknown",
        source_quote_id: Optional[str] = None,
    ) -> Quote:
        """
        Crée un objet Quote pour un haïku.

        Args:
            haiku_text: Le texte du haïku
            language: La langue du haïku
            model: Le modèle utilisé pour la génération
            source_quote_id: ID de la citation source (optionnel)

        Returns:
            Un objet Quote représentant le haïku
        """
        author_name = {
            "fr": settings.models.get_author_for_model(model, "fr"),
            "en": settings.models.get_author_for_model(model, "en"),
        }

        quote_id = f"poem_{int(datetime.now().timestamp())}"
        if source_quote_id:
            quote_id = f"poem_{source_quote_id}_{int(datetime.now().timestamp())}"

        return Quote(
            id=quote_id,
            text={
                language: haiku_text,
                "fr" if language == "en" else "en": haiku_text,
            },
            author=author_name,
            category="poem",
            type="generated",
        )

    def generate_haiku_strategy(
        self,
        quote: Quote,
        language: str,
        force_new: bool = False,
        generation_count: int = 0,
    ) -> tuple[Optional[str], str, bool]:
        """
        Détermine la stratégie de génération de haïku et l'exécute.

        Args:
            quote: Citation source
            language: Langue du haïku
            force_new: Forcer une nouvelle génération
            generation_count: Nombre de haïkus déjà générés

        Returns:
            Tuple (haiku_text, model_used, was_generated_via_api)
        """
        quote_text = quote.text.get(language, quote.text.get("fr", ""))
        quote_author = quote.author.get(language, quote.author.get("fr", ""))

        # Stratégie 1: Génération via API si demandée et possible
        if force_new and self.can_generate_new_haiku(generation_count):
            haiku_text = self.generate_via_api(quote_text, quote_author, language)
            if haiku_text:
                model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
                return haiku_text, model, True

        # Stratégie 2: Haïku stocké
        if not force_new:
            stored_haiku = self.get_stored_haiku(quote.id, language)
            if stored_haiku:
                return stored_haiku, "unknown", False

        # Stratégie 3: Fallback si force_new mais échec API ou limite atteinte
        if force_new:
            return None, "unknown", False

        # Stratégie 4: Fallback par défaut
        fallback_haiku = self.get_fallback_haiku(language)
        return fallback_haiku, "unknown", False
