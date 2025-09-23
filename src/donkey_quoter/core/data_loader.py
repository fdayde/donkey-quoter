"""
Module pour le chargement des données depuis JSON.
"""

import json
from pathlib import Path

from pydantic import ValidationError

from .models import Quote


class DataLoader:
    """Gestionnaire de chargement des données depuis JSON."""

    def load_quotes(self, path: Path) -> list[Quote]:
        """
        Charge les citations depuis un fichier JSON.

        Args:
            path: Chemin vers le fichier JSON

        Returns:
            Liste des citations validées avec Pydantic

        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            json.JSONDecodeError: Si le JSON est invalide
            ValidationError: Si les données ne respectent pas le modèle Quote
        """
        if not path.exists():
            raise FileNotFoundError(f"Le fichier {path} n'existe pas")

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Erreur de parsing JSON dans {path}: {e.msg}", e.doc, e.pos
            ) from e

        if not isinstance(data, list):
            raise ValidationError("Le fichier JSON doit contenir une liste", Quote)

        quotes = []
        for i, quote_data in enumerate(data):
            try:
                quote = Quote(**quote_data)
                quotes.append(quote)
            except ValidationError as e:
                raise ValidationError(
                    f"Erreur de validation pour la citation {i}: {e}", Quote
                ) from e

        return quotes

    def save_quotes(self, quotes: list[Quote], path: Path) -> None:
        """
        Sauvegarde les citations en JSON.

        Args:
            quotes: Liste des citations à sauvegarder
            path: Chemin vers le fichier JSON de sortie
        """
        # Créer le répertoire parent si nécessaire
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convertir les quotes en dictionnaires
        quotes_data = [quote.model_dump() for quote in quotes]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(quotes_data, f, ensure_ascii=False, indent=2)

    def get_default_quotes_path(self) -> Path:
        """
        Retourne le chemin par défaut vers le fichier quotes.json.

        Returns:
            Path vers data/quotes.json
        """
        current_dir = Path(__file__).parent
        return current_dir.parent / "data" / "quotes.json"
