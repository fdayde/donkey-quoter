"""
Module de génération de haïkus.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

from .claude_api import ClaudeAPIClient
from .config.model_mapping import get_author_for_model
from .core.haiku_service import HaikuService
from .haiku_storage import HaikuStorage
from .models import Quote
from .ui.progress_bar import ProgressBarManager


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
        self.api_client = None

        # Initialiser le compteur de session pour les haïkus
        if "haiku_generation_count" not in st.session_state:
            st.session_state.haiku_generation_count = 0

        # Initialiser le client API seulement si la clé est disponible
        try:
            self.api_client = ClaudeAPIClient()
        except ValueError as e:
            self.api_client = None
            # Stocker l'erreur pour l'afficher à l'utilisateur si nécessaire
            self.api_error = str(e)

        # Initialiser le service métier
        self.service = HaikuService(self.api_client, self.storage)

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
        # Vérifier les limites avant de commencer
        generation_count = st.session_state.haiku_generation_count
        if force_new and generation_count >= 5:
            return None

        # Afficher la barre de progression
        progress_bar = ProgressBarManager.show_generation_progress()

        try:
            # Déterminer la stratégie et générer le haïku
            haiku_text, model, was_api_call = self.service.generate_haiku_strategy(
                quote, language, force_new, generation_count
            )

            # Animer la barre de progression selon la stratégie
            if was_api_call:
                ProgressBarManager.animate_api_progress(progress_bar)
                if haiku_text:
                    # Incrémenter le compteur seulement en cas de succès
                    st.session_state.haiku_generation_count += 1
            else:
                ProgressBarManager.animate_storage_progress(progress_bar)

            # Compléter la barre de progression
            if haiku_text:
                ProgressBarManager.complete_progress(progress_bar)
            else:
                progress_bar.empty()

            # Créer l'objet Quote si on a un haïku
            if haiku_text:
                return self.service.create_haiku_quote(
                    haiku_text, language, model, quote.id
                )

            return None

        except Exception as e:
            progress_bar.empty()
            st.error(f"⚠️ {str(e)}")
            return None

    def get_usage_display(self, language: str = "fr") -> str:
        """Retourne l'affichage du compteur d'usage."""
        count = st.session_state.haiku_generation_count
        remaining = max(0, 5 - count)

        if language == "fr":
            return f"Haïkus restants : {remaining}/5"
        else:
            return f"Haikus remaining: {remaining}/5"
