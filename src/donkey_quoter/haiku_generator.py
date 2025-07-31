"""
Module de génération de haïkus.
"""

import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

from .api_limiter import APILimiter
from .claude_api import ClaudeAPIClient
from .haiku_storage import HaikuStorage
from .models import Quote


class HaikuGenerator:
    """Générateur de haïkus basé sur les citations."""

    # Haïkus de fallback génériques si aucun haïku n'est disponible
    FALLBACK_HAIKUS = {
        "fr": [
            "Âne philosophe\nMédite sous le vieux chêne\nSagesse simple",
            "Baudet tranquille\nPorte le poids de la vie\nPas après pas",
            "Oreilles dressées\nÉcoutent le vent qui passe\nMoment présent",
        ],
        "en": [
            "Donkey philosopher\nMeditates under old oak\nSimple wisdom flows",
            "Peaceful mule carries\nLife's burden step by step\nQuiet strength endures",
            (
                "Ears raised high, listening\n"
                "To the passing wind's whisper\n"
                "Present moment speaks"
            ),
        ],
    }

    def __init__(self, data_dir: Path = None):
        """Initialise le générateur de haïkus."""
        self.storage = HaikuStorage(data_dir)
        self.limiter = APILimiter(data_dir)
        self.api_client = None

        # Initialiser le client API seulement si la clé est disponible
        try:
            self.api_client = ClaudeAPIClient()
        except ValueError:
            print(
                "API Claude non configurée - utilisation des haïkus stockés uniquement"
            )

    def generate_from_quote(
        self, quote: Quote, language: str, force_new: bool = False
    ) -> Optional[Quote]:
        """
        Génère un haïku basé sur une citation.

        Args:
            quote: La citation source
            language: La langue du haïku
            force_new: Si True, essaie toujours de générer un nouveau haïku via API

        Returns:
            Un objet Quote contenant le haïku ou None en cas d'erreur
        """
        quote_text = quote.text.get(language, quote.text.get("fr", ""))
        quote_author = quote.author.get(language, quote.author.get("fr", ""))

        # Vérifier si on peut/doit utiliser l'API
        use_api = False
        api_message = ""

        if self.api_client and (
            force_new or not self.storage.has_haiku(quote.id, language)
        ):
            can_use, message = self.limiter.can_use_api()
            if can_use:
                use_api = True
            else:
                api_message = message

        # Afficher la progress bar
        progress_bar = st.progress(0)

        if use_api:
            # Générer via API Claude
            for i in range(50):
                time.sleep(0.02)
                progress_bar.progress(i + 1)

            haiku_text = self.api_client.generate_haiku(
                quote_text, quote_author, language
            )

            if haiku_text:
                # Sauvegarder le haïku généré
                self.storage.add_haiku(quote.id, haiku_text, language)
                self.limiter.increment_usage()

                for i in range(50, 100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
            else:
                # Échec de l'API, utiliser le stockage
                use_api = False
                for i in range(50, 100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)

        if not use_api:
            # Utiliser un haïku stocké
            for i in range(100):
                time.sleep(0.015)
                progress_bar.progress(i + 1)

            haiku_text = self.storage.get_haiku(quote.id, language)

            if not haiku_text:
                # Aucun haïku stocké, utiliser un fallback
                haiku_text = random.choice(self.FALLBACK_HAIKUS[language])

                if api_message:
                    st.warning(f"⚠️ {api_message}")

        progress_bar.empty()

        # Créer le poème avec l'auteur approprié
        author_name = {
            "fr": "Claude Haiku" if use_api else "Maître du Haïku",
            "en": "Claude Haiku" if use_api else "Haiku Master",
        }

        poem = Quote(
            id=f"poem_{int(datetime.now().timestamp())}",
            text={
                language: haiku_text,
                "fr" if language == "en" else "en": haiku_text,
            },
            author=author_name,
            category="poem",
            type="generated",
        )

        return poem

    def get_usage_display(self, language: str = "fr") -> str:
        """Retourne l'affichage du compteur d'usage."""
        return self.limiter.get_usage_display(language)
