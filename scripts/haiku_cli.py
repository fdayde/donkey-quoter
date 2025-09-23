"""
CLI unifié pour la gestion des haïkus.
"""

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.donkey_quoter.core.haiku_manager import HaikuManager
from src.donkey_quoter.infrastructure.anthropic_client import AnthropicClient
from src.donkey_quoter.ui.cli_display import (
    print_error,
    print_progress,
    print_stats,
    print_success,
)


def setup_utf8_windows():
    """Configure UTF-8 pour Windows."""
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def create_api_client(dry_run: bool, model: str = None) -> tuple:
    """Crée le client API si nécessaire."""
    if dry_run:
        return None, None

    try:
        api_client = AnthropicClient(model=model)
        return api_client, api_client.model
    except ValueError as e:
        print_error(f"Erreur API : {e}")
        sys.exit(1)


def cmd_generate(args, manager: HaikuManager, model: str):
    """Commande generate - mode batch bilingue uniquement."""
    print("\n🚀 Génération de haïkus (FR + EN)")
    if model:
        print(f"   Modèle : {model}")

    mode = "RÉGÉNÉRATION COMPLÈTE" if args.all else "GÉNÉRATION DES MANQUANTS"
    print(f"   Mode : {mode}")

    # Mode batch bilingue uniquement
    quotes = manager.get_quotes_for_batch(args.all)
    if args.limit:
        quotes = quotes[: args.limit]

    if not quotes:
        print_success("Tous les haïkus sont déjà générés !")
        return

    print(f"\n📊 Citations à traiter : {len(quotes)}")

    # Estimation coût
    if model:
        cost_info = manager.calculate_cost_estimate(len(quotes))
        if cost_info["cost"] > 0:
            cost = cost_info["cost"]
            method = cost_info["method"]

            if method == "count_tokens":
                method_text = "count_tokens() précis"
                tokens_info = f" ({cost_info['input_tokens']:,} input + {cost_info['output_tokens']:,} output)"
            else:
                method_text = "estimation basique"
                tokens_info = f" (~{cost_info['total_tokens']:,} tokens)"

            print(f"   Coût estimé : ${cost:.4f} USD")
            print(f"   Méthode : {method_text}{tokens_info}")

    if not args.dry_run and not args.yes:
        if input("\nContinuer ? (o/n) : ").strip().lower() != "o":
            print("❌ Annulé")
            return

    print("\n🚀 Génération en cours...")
    success_count = error_count = 0
    batch_size = 5

    for i in range(0, len(quotes), batch_size):
        batch = quotes[i : i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(quotes) + batch_size - 1) // batch_size

        print_progress(batch_num, total_batches, f"Batch {batch_num}/{total_batches}")

        try:
            haikus = manager.generate_batch(batch)

            for quote in batch:
                if (
                    quote.id in haikus
                    and haikus[quote.id].get("fr")
                    and haikus[quote.id].get("en")
                ):
                    if not args.dry_run:
                        manager.storage.add_haiku(
                            quote.id, haikus[quote.id]["fr"], "fr", model
                        )
                        manager.storage.add_haiku(
                            quote.id, haikus[quote.id]["en"], "en", model
                        )
                    success_count += 2
                else:
                    error_count += 2

            if not args.dry_run and batch_num < total_batches:
                time.sleep(1.0)

        except Exception as e:
            print_error(f"Batch {batch_num}: {e}")
            error_count += len(batch) * 2

    print(f"\n\n✨ Terminé ! Haïkus générés: {success_count}, Échecs: {error_count}")


def cmd_stats(manager: HaikuManager):
    """Commande stats."""
    stats = manager.get_statistics()
    print_stats(stats)


def cmd_export(args, manager: HaikuManager):
    """Commande export."""
    format_type = args.format or "json"
    output_file = args.output or f"haikus_export.{format_type}"

    data = manager.export_data(format_type)

    if format_type == "json":
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    elif format_type == "csv":
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(data["headers"])
            writer.writerows(data["rows"])

    print_success(f"Export {format_type.upper()} créé : {output_file}")


def main():
    """Point d'entrée principal."""
    setup_utf8_windows()

    parser = argparse.ArgumentParser(
        description="CLI unifié pour la gestion des haïkus"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simulation sans appel API"
    )
    parser.add_argument("--model", help="Modèle Claude à utiliser")

    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Commande generate
    gen_parser = subparsers.add_parser("generate", help="Génère des haïkus (FR + EN)")
    gen_parser.add_argument(
        "--all", action="store_true", help="Régénérer tous les haïkus"
    )
    gen_parser.add_argument("--limit", type=int, help="Limiter le nombre de citations")
    gen_parser.add_argument(
        "-y", "--yes", action="store_true", help="Pas de confirmation"
    )

    # Commande stats
    subparsers.add_parser("stats", help="Affiche les statistiques")

    # Commande export
    export_parser = subparsers.add_parser("export", help="Exporte les haïkus")
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Format d'export"
    )
    export_parser.add_argument("--output", help="Fichier de sortie")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Charger env et vérifier API key si nécessaire
    load_dotenv()
    if not args.dry_run and args.command == "generate":
        api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print_error("CLAUDE_API_KEY ou ANTHROPIC_API_KEY non définie dans .env")
            sys.exit(1)

    # Créer manager
    api_client, model = create_api_client(args.dry_run, args.model)
    manager = HaikuManager(api_client)

    # Exécuter commande
    if args.command == "generate":
        cmd_generate(args, manager, model)
    elif args.command == "stats":
        cmd_stats(manager)
    elif args.command == "export":
        cmd_export(args, manager)


if __name__ == "__main__":
    main()
