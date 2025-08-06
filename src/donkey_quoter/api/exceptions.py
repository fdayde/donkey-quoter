"""
Exceptions et gestion d'erreurs pour les APIs.
"""

from anthropic import APIError, APITimeoutError, RateLimitError


class APIErrorHandler:
    """Gestionnaire centralisé des erreurs API."""

    @staticmethod
    def handle_api_error(error: Exception) -> Exception:
        """
        Convertit les erreurs API en messages d'erreur utilisateur.

        Args:
            error: L'exception originale

        Returns:
            Exception avec un message utilisateur approprié
        """
        if isinstance(error, RateLimitError):
            return Exception(
                "Limite de crédit API atteinte. Veuillez vérifier votre compte Anthropic."
            )

        if isinstance(error, APITimeoutError):
            return Exception(
                "Délai d'attente dépassé. Vérifiez votre connexion internet."
            )

        if isinstance(error, APIError):
            error_msg = str(error).lower()
            if "unauthorized" in error_msg or "api_key" in error_msg:
                return Exception(
                    "Clé API invalide. Veuillez vérifier votre configuration."
                )
            else:
                return Exception(f"Erreur API : {str(error)[:100]}...")

        # Autres erreurs génériques
        error_msg = str(error).lower()
        if "connection" in error_msg or "network" in error_msg:
            return Exception("Erreur de connexion. Vérifiez votre connexion internet.")
        else:
            return Exception(f"Erreur lors de la génération : {str(error)[:100]}...")
