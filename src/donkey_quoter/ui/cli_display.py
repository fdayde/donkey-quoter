"""
Utilitaires d'affichage pour CLI.
Simple et focalisé (KISS).
"""

from typing import Any


def print_progress(current: int, total: int, message: str = ""):
    """Affiche une barre de progression simple."""
    if total == 0:
        return

    percentage = int((current / total) * 100)
    bar_length = 20
    filled_length = int(bar_length * current // total)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)
    print(
        f"\r[{bar}] {percentage:3d}% ({current}/{total}) {message}", end="", flush=True
    )


def print_stats(stats: dict[str, Any]):
    """Affiche les statistiques."""
    print("\n📊 Statistiques des haïkus")
    print("=" * 40)

    # Stats par langue
    for lang, data in stats["languages"].items():
        print(f"\n{lang.upper()}:")
        print(
            f"   Avec haïku    : {data['with_haiku']:3d} ({data['percentage']:5.1f}%)"
        )
        print(f"   Sans haïku    : {data['without_haiku']:3d}")

    # Stats bilingues
    bilingual = stats["bilingual"]
    print("\nBILINGUE:")
    print(
        f"   Complets (FR+EN) : {bilingual['complete']:3d} ({bilingual['percentage']:5.1f}%)"
    )

    # Modèles utilisés
    if stats["models_used"]:
        print("\nMODÈLES UTILISÉS:")
        for model in stats["models_used"]:
            print(f"   - {model}")

    print(f"\nTOTAL : {stats['total_quotes']} citations")


def print_error(message: str):
    """Affiche une erreur."""
    print(f"❌ {message}")


def print_success(message: str):
    """Affiche un succès."""
    print(f"✅ {message}")


def print_info(message: str):
    """Affiche une info."""
    print(f"ℹ️  {message}")
