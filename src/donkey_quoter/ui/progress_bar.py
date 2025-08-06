"""
Composants UI pour les barres de progression.
"""

import time
from typing import Any

import streamlit as st


class ProgressBarManager:
    """Gestionnaire des barres de progression."""

    @staticmethod
    def show_generation_progress() -> Any:
        """
        Affiche une barre de progression pour la génération.

        Returns:
            L'objet progress bar pour mise à jour
        """
        return st.progress(0)

    @staticmethod
    def animate_api_progress(progress_bar: Any):
        """
        Anime la barre de progression pendant l'appel API.

        Args:
            progress_bar: La barre de progression à animer
        """
        for i in range(50):
            time.sleep(0.02)
            progress_bar.progress(i + 1)

    @staticmethod
    def animate_storage_progress(progress_bar: Any):
        """
        Anime la barre de progression pour la récupération depuis le stockage.

        Args:
            progress_bar: La barre de progression à animer
        """
        for i in range(100):
            time.sleep(0.015)
            progress_bar.progress(i + 1)

    @staticmethod
    def complete_progress(progress_bar: Any):
        """
        Termine l'animation de la barre de progression.

        Args:
            progress_bar: La barre de progression à compléter
        """
        for i in range(50, 100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        progress_bar.empty()
