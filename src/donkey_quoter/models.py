"""
Modèles de données pour l'application.
"""
from typing import Dict, Optional

from pydantic import BaseModel, Field


class Quote(BaseModel):
    """Modèle pour une citation."""

    id: str
    text: Dict[str, str]
    author: Dict[str, str]
    category: str = Field(pattern="^(classic|personal|humor|poem)$")
    type: str = Field(pattern="^(preset|user|generated)$")


class QuoteInput(BaseModel):
    """Modèle pour l'ajout d'une citation."""

    text: str = Field(min_length=1)
    author: str = Field(min_length=1)
    category: str = Field(default="personal", pattern="^(classic|personal|humor)$")