"""
Module pour gérer les limites de débit de l'API count_tokens d'Anthropic.
"""

import os
import time


class TokenCounter:
    """Gestionnaire simple des limites de débit pour count_tokens()."""

    def __init__(self):
        """Initialise le compteur en lisant le tier depuis l'environnement."""
        # Lire le tier depuis l'environnement (défaut: 1)
        tier = int(os.getenv("ANTHROPIC_TIER", "1"))

        # Limites par tier avec marge de sécurité (80%)
        tier_limits = {1: 80, 2: 800, 3: 1600, 4: 3200, 5: 6400}
        self.limit = tier_limits.get(tier, 80)

        self.count_calls = 0
        self.last_reset = time.time()

    def can_count_tokens(self) -> bool:
        """Vérifie si on peut appeler count_tokens."""
        # Reset après 60 secondes
        if time.time() - self.last_reset >= 60:
            self.count_calls = 0
            self.last_reset = time.time()

        return self.count_calls < self.limit

    def increment(self):
        """Incrémente le compteur après un appel."""
        self.count_calls += 1

    def get_reset_time(self) -> int:
        """
        Retourne le temps d'attente avant le prochain reset (en secondes).

        Returns:
            Nombre de secondes avant le reset (arrondi vers le haut).
        """
        elapsed = time.time() - self.last_reset
        return max(0, int(60 - elapsed) + 1)  # +1 pour arrondir vers le haut
