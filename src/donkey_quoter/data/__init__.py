"""Module de données."""

from ..core.data_loader import DataLoader

# Charger les citations depuis JSON
_data_loader = DataLoader()
CLASSIC_QUOTES = [
    quote.model_dump()
    for quote in _data_loader.load_quotes(_data_loader.get_default_quotes_path())
]

__all__ = ["CLASSIC_QUOTES"]
