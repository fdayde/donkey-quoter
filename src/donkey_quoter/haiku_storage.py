"""
Module de gestion du stockage des haïkus générés.
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Union


class HaikuStorage:
    """Gestionnaire du stockage des haïkus générés pour chaque citation."""

    def __init__(self, data_dir: Path = None):
        """
        Initialise le gestionnaire de stockage.

        Args:
            data_dir: Répertoire pour stocker les haïkus
        """
        self.data_dir = data_dir or Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.haikus_file = self.data_dir / "haikus.json"

        # Charger les haïkus existants
        self.haikus_data = self._load_haikus()

    def _load_haikus(self) -> dict[str, dict[str, list[Union[str, dict]]]]:
        """
        Charge les haïkus depuis le fichier.

        Returns:
            Dict au format {quote_id: {lang: [haiku_data, ...]}}
        """
        if self.haikus_file.exists():
            try:
                with open(self.haikus_file, encoding="utf-8") as f:
                    data = json.load(f)
                    # Convertir l'ancien format si nécessaire
                    return self._migrate_old_format(data)
            except Exception as e:
                print(f"Erreur lors du chargement des haïkus : {e}")
                return {}
        return {}

    def _migrate_old_format(self, data: dict) -> dict:
        """
        Migre l'ancien format (string simple) vers le nouveau (avec métadonnées).
        """
        migrated_data = {}

        for quote_id, languages in data.items():
            migrated_data[quote_id] = {}

            for lang, haikus in languages.items():
                migrated_data[quote_id][lang] = []

                for haiku in haikus:
                    if isinstance(haiku, str):
                        # Ancien format : convertir en nouveau format
                        migrated_data[quote_id][lang].append(
                            {
                                "text": haiku,
                                "generated_at": "2024-01-01T00:00:00Z",
                                "model": "unknown",  # Modèle inconnu pour les anciens
                            }
                        )
                    else:
                        # Déjà au nouveau format
                        migrated_data[quote_id][lang].append(haiku)

        return migrated_data

    def _save_haikus(self):
        """Sauvegarde les haïkus dans le fichier."""
        with open(self.haikus_file, "w", encoding="utf-8") as f:
            json.dump(self.haikus_data, f, ensure_ascii=False, indent=2)

    def get_haiku(self, quote_id: str, language: str) -> Optional[str]:
        """
        Récupère un haïku pour une citation donnée.

        Args:
            quote_id: ID de la citation
            language: Langue du haïku ('fr' ou 'en')

        Returns:
            Un haïku aléatoire ou None si aucun n'existe
        """
        if quote_id in self.haikus_data:
            haikus = self.haikus_data[quote_id].get(language, [])
            if haikus:
                haiku_data = random.choice(haikus)
                # Retourner juste le texte pour compatibilité
                if isinstance(haiku_data, dict):
                    return haiku_data.get("text")
                return haiku_data  # Ancien format
        return None

    def add_haiku(self, quote_id: str, haiku: str, language: str, model: str = None):
        """
        Ajoute un haïku pour une citation avec métadonnées.

        Args:
            quote_id: ID de la citation
            haiku: Le haïku à ajouter
            language: Langue du haïku
            model: Modèle utilisé pour générer le haïku
        """
        if quote_id not in self.haikus_data:
            self.haikus_data[quote_id] = {"fr": [], "en": []}

        if language not in self.haikus_data[quote_id]:
            self.haikus_data[quote_id][language] = []

        # Créer l'entrée avec métadonnées
        haiku_entry = {
            "text": haiku,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "model": model or "unknown",
        }

        # Éviter les doublons (basé sur le texte)
        existing_texts = [
            h.get("text") if isinstance(h, dict) else h
            for h in self.haikus_data[quote_id][language]
        ]

        if haiku not in existing_texts:
            self.haikus_data[quote_id][language].append(haiku_entry)
            self._save_haikus()

    def has_haiku(self, quote_id: str, language: str) -> bool:
        """
        Vérifie si un haïku existe pour une citation.

        Args:
            quote_id: ID de la citation
            language: Langue du haïku

        Returns:
            True si au moins un haïku existe
        """
        return (
            quote_id in self.haikus_data
            and language in self.haikus_data[quote_id]
            and len(self.haikus_data[quote_id][language]) > 0
        )

    def get_all_haikus(self, quote_id: str, language: str) -> list[dict]:
        """
        Récupère tous les haïkus avec métadonnées pour une citation.

        Args:
            quote_id: ID de la citation
            language: Langue des haïkus

        Returns:
            Liste de dicts avec text, generated_at, model
        """
        if quote_id in self.haikus_data:
            haikus = self.haikus_data[quote_id].get(language, [])
            # Convertir au format uniforme
            result = []
            for h in haikus:
                if isinstance(h, dict):
                    result.append(h)
                else:
                    # Ancien format
                    result.append(
                        {"text": h, "generated_at": "unknown", "model": "unknown"}
                    )
            return result
        return []

    def count_haikus(self, quote_id: str, language: str) -> int:
        """
        Compte le nombre de haïkus pour une citation.

        Args:
            quote_id: ID de la citation
            language: Langue des haïkus

        Returns:
            Nombre de haïkus
        """
        return len(self.get_all_haikus(quote_id, language))

    def get_missing_quotes(self, all_quote_ids: list[str], language: str) -> list[str]:
        """
        Retourne les IDs des citations sans haïku.

        Args:
            all_quote_ids: Liste de tous les IDs de citations
            language: Langue à vérifier

        Returns:
            Liste des IDs sans haïku
        """
        missing = []
        for quote_id in all_quote_ids:
            if not self.has_haiku(quote_id, language):
                missing.append(quote_id)
        return missing

    def export_haikus(self) -> str:
        """
        Exporte tous les haïkus en JSON.

        Returns:
            String JSON des haïkus
        """
        return json.dumps(self.haikus_data, ensure_ascii=False, indent=2)

    def import_haikus(self, json_data: str):
        """
        Importe des haïkus depuis une chaîne JSON.

        Args:
            json_data: Données JSON à importer
        """
        try:
            imported_data = json.loads(json_data)
            # Fusionner avec les données existantes
            for quote_id, languages in imported_data.items():
                if quote_id not in self.haikus_data:
                    self.haikus_data[quote_id] = {"fr": [], "en": []}

                for lang, haikus in languages.items():
                    if lang not in self.haikus_data[quote_id]:
                        self.haikus_data[quote_id][lang] = []

                    # Ajouter sans doublons (basé sur le texte)
                    existing_texts = [
                        h.get("text") if isinstance(h, dict) else h
                        for h in self.haikus_data[quote_id][lang]
                    ]

                    for haiku in haikus:
                        haiku_text = (
                            haiku.get("text") if isinstance(haiku, dict) else haiku
                        )
                        if haiku_text not in existing_texts:
                            self.haikus_data[quote_id][lang].append(haiku)

            self._save_haikus()
        except Exception as e:
            print(f"Erreur lors de l'import des haïkus : {e}")
            raise
