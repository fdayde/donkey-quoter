"""
Module de génération de haïkus.
"""

import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

from .api_limiter import APILimiter
from .claude_api import ClaudeAPIClient
from .config.model_mapping import get_author_for_model
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

    def get_existing_haiku(self, quote: Quote, language: str) -> Optional[Quote]:
        """
        Récupère un haïku existant pour une citation.

        Args:
            quote: La citation source
            language: La langue du haïku

        Returns:
            Un objet Quote contenant le haïku ou None si aucun n'existe
        """
        # Récupérer le haïku avec ses métadonnées
        haiku_data = self.storage.get_haiku_with_metadata(quote.id, language)

        if not haiku_data:
            return None

        # Déterminer l'auteur basé sur le modèle
        model = haiku_data.get("model", "unknown")
        author_name = get_author_for_model(model, language)

        # Créer le poème avec les bonnes métadonnées
        poem = Quote(
            id=f"poem_{quote.id}_{int(datetime.now().timestamp())}",
            text={
                language: haiku_data.get("text", ""),
                "fr" if language == "en" else "en": haiku_data.get("text", ""),
            },
            author={
                "fr": author_name
                if language == "fr"
                else get_author_for_model(model, "fr"),
                "en": author_name
                if language == "en"
                else get_author_for_model(model, "en"),
            },
            category="poem",
            type="generated",  # Utiliser "generated" car le haïku a été généré
        )

        return poem

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

        # Si force_new=True, toujours essayer de générer un nouveau haïku
        if self.api_client and force_new:
            can_use, message = self.limiter.can_use_api()
            if can_use:
                use_api = True
            else:
                api_message = message
                st.warning(f"⚠️ {api_message}")
                return None

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
                model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
                self.storage.add_haiku(quote.id, haiku_text, language, model)
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

        # Déterminer le modèle utilisé
        if use_api:
            model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        else:
            # Si on n'a pas utilisé l'API mais qu'on force la génération, on n'a pas de haïku
            if force_new:
                return None
            # Sinon, utiliser un fallback générique
            model = "unknown"

        # Créer le poème avec l'auteur approprié basé sur le modèle
        author_name = {
            "fr": get_author_for_model(model, "fr"),
            "en": get_author_for_model(model, "en"),
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
