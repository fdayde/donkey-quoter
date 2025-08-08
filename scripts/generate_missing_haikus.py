"""
Script pour générer des haïkus pour les citations qui n'en ont pas.
"""

import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from src.donkey_quoter.core.models import Quote
from src.donkey_quoter.core.storage import DataStorage
from src.donkey_quoter.data.quotes import CLASSIC_QUOTES
from src.donkey_quoter.infrastructure.anthropic_client import AnthropicClient
from src.donkey_quoter.prompts.haiku_prompts import build_haiku_prompt


def generate_missing_haikus(languages=None, limit=None):
    """
    Génère des haïkus pour toutes les citations qui n'en ont pas.

    Args:
        languages: Liste des langues pour lesquelles générer des haïkus
        limit: Nombre maximum de haïkus à générer (None = tous)
    """
    # Initialiser les langues par défaut
    if languages is None:
        languages = ["fr", "en"]

    # Initialiser les composants
    storage = DataStorage(Path("data"))

    try:
        api_client = AnthropicClient()
    except ValueError as e:
        print(f"Erreur : {e}")
        print("Veuillez configurer ANTHROPIC_API_KEY dans le fichier .env")
        return

    # Récupérer toutes les citations
    quotes = [Quote(**q) for q in CLASSIC_QUOTES]

    # Trouver les citations sans haïku
    missing_haikus = []
    for quote in quotes:
        for lang in languages:
            if not storage.has_haiku(quote.id, lang):
                missing_haikus.append((quote, lang))

    if not missing_haikus:
        print("Toutes les citations ont déjà des haïkus !")
        return

    print(f"Citations sans haïku : {len(missing_haikus)}")

    if limit:
        missing_haikus = missing_haikus[:limit]
        print(f"Limitation à {limit} générations")

    # Générer les haïkus manquants
    generated = 0
    failed = 0

    for i, (quote, lang) in enumerate(missing_haikus, 1):
        quote_text = quote.text.get(lang, quote.text.get("fr", ""))
        quote_author = quote.author.get(lang, quote.author.get("fr", ""))

        print(f"\n[{i}/{len(missing_haikus)}] Génération pour {quote.id} ({lang})")
        print(f"  Citation : {quote_text[:50]}...")

        try:
            # Construire le prompt avec le module dédié
            prompt = build_haiku_prompt(quote_text, quote_author, lang)

            # Appel générique à l'API
            haiku = api_client.call_claude(prompt)

            if haiku:
                storage.add_haiku(quote.id, haiku, lang)
                print(f"  ✓ Haïku généré : {haiku.split()[0]}...")
                generated += 1
            else:
                print("  ✗ Échec de la génération")
                failed += 1

        except Exception as e:
            print(f"  ✗ Erreur : {e}")
            failed += 1

        # Pause entre les appels pour éviter de surcharger l'API
        if i < len(missing_haikus):
            time.sleep(1)

    # Résumé
    print(f"\n{'=' * 50}")
    print("Génération terminée :")
    print(f"  - Haïkus générés : {generated}")
    print(f"  - Échecs : {failed}")
    print(f"  - Total citations : {len(quotes)}")

    # Afficher les statistiques finales
    print("\nStatistiques par langue :")
    for lang in languages:
        count = sum(1 for q in quotes if storage.has_haiku(q.id, lang))
        print(f"  - {lang.upper()} : {count}/{len(quotes)} citations avec haïku")


def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Génère des haïkus pour les citations sans haïku"
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["fr", "en"],
        help="Langues pour lesquelles générer des haïkus (défaut: fr en)",
    )
    parser.add_argument("--limit", type=int, help="Nombre maximum de haïkus à générer")

    args = parser.parse_args()

    generate_missing_haikus(args.languages, args.limit)


if __name__ == "__main__":
    main()
