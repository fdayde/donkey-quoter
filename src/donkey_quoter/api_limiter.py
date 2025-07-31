"""
Module de gestion des limites d'utilisation de l'API.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st


class APILimiter:
    """Gestionnaire des limites d'utilisation de l'API Claude."""

    def __init__(self, data_dir: Path = None):
        """
        Initialise le limiteur d'API.

        Args:
            data_dir: Répertoire pour stocker les données de limite
        """
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.limits_file = self.data_dir / "api_limits.json"

        # Limites configurables
        self.session_limit = int(os.getenv("SESSION_LIMIT", "10"))
        self.daily_limit = int(os.getenv("DAILY_LIMIT", "10"))

        # Charger les données existantes
        self.limits_data = self._load_limits()

        # Initialiser le compteur de session dans Streamlit
        if "api_usage_session" not in st.session_state:
            st.session_state.api_usage_session = 0

    def _load_limits(self) -> dict:
        """Charge les données de limites depuis le fichier."""
        if self.limits_file.exists():
            try:
                with open(self.limits_file) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_limits(self):
        """Sauvegarde les données de limites dans le fichier."""
        with open(self.limits_file, "w") as f:
            json.dump(self.limits_data, f, indent=2)

    def _get_today_key(self) -> str:
        """Retourne la clé pour aujourd'hui."""
        return datetime.now().strftime("%Y-%m-%d")

    def _cleanup_old_data(self):
        """Nettoie les données de plus de 7 jours."""
        today = datetime.now()
        keys_to_remove = []

        for date_key in self.limits_data.keys():
            try:
                date_obj = datetime.strptime(date_key, "%Y-%m-%d")
                if (today - date_obj).days > 7:
                    keys_to_remove.append(date_key)
            except ValueError:
                continue

        for key in keys_to_remove:
            del self.limits_data[key]

        if keys_to_remove:
            self._save_limits()

    def can_use_api(self) -> tuple[bool, str]:
        """
        Vérifie si l'API peut être utilisée.

        Returns:
            Tuple (peut_utiliser, message)
        """
        # Nettoyer les anciennes données
        self._cleanup_old_data()

        # Vérifier limite de session
        session_usage = st.session_state.api_usage_session
        if session_usage >= self.session_limit:
            return (
                False,
                f"Limite de session atteinte ({self.session_limit} générations)",
            )

        # Vérifier limite quotidienne
        today_key = self._get_today_key()
        daily_usage = self.limits_data.get(today_key, 0)
        if daily_usage >= self.daily_limit:
            return (
                False,
                f"Limite quotidienne atteinte ({self.daily_limit} générations)",
            )

        return True, "OK"

    def increment_usage(self):
        """Incrémente les compteurs d'utilisation."""
        # Incrémenter session
        st.session_state.api_usage_session += 1

        # Incrémenter quotidien
        today_key = self._get_today_key()
        self.limits_data[today_key] = self.limits_data.get(today_key, 0) + 1
        self._save_limits()

    def get_usage_stats(self) -> dict[str, int]:
        """
        Retourne les statistiques d'utilisation.

        Returns:
            Dict avec les compteurs actuels
        """
        today_key = self._get_today_key()
        return {
            "session_current": st.session_state.api_usage_session,
            "session_limit": self.session_limit,
            "daily_current": self.limits_data.get(today_key, 0),
            "daily_limit": self.daily_limit,
        }

    def reset_session_counter(self):
        """Réinitialise le compteur de session."""
        st.session_state.api_usage_session = 0

    def get_usage_display(self, language: str = "fr") -> str:
        """
        Retourne un affichage formaté des limites.

        Args:
            language: Langue d'affichage ('fr' ou 'en')

        Returns:
            Chaîne formatée pour l'affichage
        """
        stats = self.get_usage_stats()

        if language == "fr":
            return (
                f"Générations : {stats['session_current']}/{stats['session_limit']} "
                f"(session) | {stats['daily_current']}/{stats['daily_limit']} (jour)"
            )
        else:
            return (
                f"Generations: {stats['session_current']}/{stats['session_limit']} "
                f"(session) | {stats['daily_current']}/{stats['daily_limit']} (day)"
            )
