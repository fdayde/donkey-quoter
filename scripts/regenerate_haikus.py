"""
Script optimisé pour régénérer les haïkus avec Claude 3.5 Haiku.
Utilise le batch processing et la génération bilingue pour réduire les coûts.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.donkey_quoter.claude_api import ClaudeAPIClient
from src.donkey_quoter.config.api_pricing import CLAUDE_PRICING, TOKEN_ESTIMATION
from src.donkey_quoter.data.quotes import CLASSIC_QUOTES
from src.donkey_quoter.haiku_storage import HaikuStorage
from src.donkey_quoter.models import Quote


class OptimizedHaikuRegenerator:
    """Classe optimisée pour régénérer les haïkus par batch."""

    BATCH_SIZE = 5  # Nombre de citations par batch

    def __init__(self, dry_run: bool = False):
        """Initialise le régénérateur optimisé."""
        self.dry_run = dry_run
        self.storage = HaikuStorage()
        self.api_client = None
        self.model = os.getenv("CLAUDE_MODEL_HAIKU", "claude-3-5-haiku-20241022")

        # Métriques d'utilisation globales
        self.total_metrics = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_cost": 0.0,
            "batches_processed": 0,
        }

        if not dry_run:
            try:
                # Utiliser temporairement le modèle Haiku 3.5
                original_model = os.getenv("CLAUDE_MODEL")
                os.environ["CLAUDE_MODEL"] = self.model
                self.api_client = ClaudeAPIClient()
                # Restaurer le modèle original
                if original_model:
                    os.environ["CLAUDE_MODEL"] = original_model
                else:
                    del os.environ["CLAUDE_MODEL"]
            except ValueError as e:
                print(f"❌ Erreur : {e}")
                sys.exit(1)

    def get_existing_haikus(self) -> dict[str, dict[str, list[str]]]:
        """Charge les haïkus existants."""
        try:
            return self.storage.haikus_data
        except Exception:
            return {}

    def needs_regeneration(self, quote_id: str, regenerate_all: bool) -> bool:
        """Détermine si un haïku doit être régénéré."""
        if regenerate_all:
            return True

        existing = self.storage.haikus_data.get(quote_id, {})
        # Vérifier si les haïkus existent pour les deux langues
        return not (existing.get("fr") and existing.get("en"))

    def create_batch_prompt(self, quotes: list[Quote]) -> str:
        """Crée un prompt optimisé pour générer plusieurs haïkus bilingues."""
        prompt = (
            "Génère des haïkus poétiques en français ET en anglais "
            "pour chaque citation.\n\n"
            "Format de sortie JSON strict :\n"
            "{\n"
            '  "quote_id": {\n'
            '    "fr": "haïku en français (3 lignes, format 5-7-5 syllabes)",\n'
            '    "en": "haiku in English (3 lines, 5-7-5 syllables)"\n'
            "  }\n"
            "}\n\n"
            "Citations à traiter :\n"
        )

        for quote in quotes:
            prompt += f"\nID: {quote.id}\n"
            prompt += f'FR: "{quote.text["fr"]}" - {quote.author["fr"]}\n'
            prompt += f'EN: "{quote.text["en"]}" - {quote.author["en"]}\n'

        prompt += (
            "\nGénère un haïku unique et poétique pour chaque "
            "citation, inspiré par son message."
        )

        return prompt

    def parse_batch_response(
        self, response: str, quote_ids: list[str]
    ) -> dict[str, dict[str, str]]:
        """Parse la réponse JSON du batch."""
        try:
            # Extraire le JSON de la réponse
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception:
            return {}

    def estimate_batch_tokens(self, quotes: list[Quote]) -> dict[str, int]:
        """Estime les tokens pour un batch de citations."""
        prompt = self.create_batch_prompt(quotes)
        input_tokens = len(prompt) // TOKEN_ESTIMATION["chars_per_token"]
        # Output : environ 150 tokens par haïku × 2 langues × nombre de citations
        output_tokens = TOKEN_ESTIMATION["haiku_output_tokens"] * 2 * len(quotes)

        return {
            "input": input_tokens,
            "output": output_tokens,
            "total": input_tokens + output_tokens,
        }

    def calculate_savings(
        self, total_quotes: int, skipped_quotes: int
    ) -> dict[str, float]:
        """Calcule les économies réalisées."""
        # Coût sans optimisation
        tokens_per_quote = TOKEN_ESTIMATION["haiku_output_tokens"] + 100  # approx input
        tokens_unoptimized = total_quotes * 2 * tokens_per_quote  # 2 langues
        cost_unoptimized = (tokens_unoptimized / 1_000_000) * CLAUDE_PRICING[
            self.model
        ]["output"]

        # Coût avec optimisation
        quotes_to_process = total_quotes - skipped_quotes
        batches = (quotes_to_process + self.BATCH_SIZE - 1) // self.BATCH_SIZE
        tokens_optimized = (
            batches * self.BATCH_SIZE * 2 * TOKEN_ESTIMATION["haiku_output_tokens"]
        )
        cost_optimized = (tokens_optimized / 1_000_000) * CLAUDE_PRICING[self.model][
            "output"
        ]

        return {
            "unoptimized": cost_unoptimized,
            "optimized": cost_optimized,
            "saved": cost_unoptimized - cost_optimized,
            "percentage": ((cost_unoptimized - cost_optimized) / cost_unoptimized * 100)
            if cost_unoptimized > 0
            else 0,
        }

    def display_estimation(self, quotes: list[dict], regenerate_all: bool):
        """Affiche l'estimation optimisée des coûts."""
        quotes_to_process = []

        for quote_data in quotes:
            quote = Quote(**quote_data)
            if self.needs_regeneration(quote.id, regenerate_all):
                quotes_to_process.append(quote)

        skipped = len(quotes) - len(quotes_to_process)
        batches = (len(quotes_to_process) + self.BATCH_SIZE - 1) // self.BATCH_SIZE

        print("\n🚀 Régénération OPTIMISÉE des haïkus avec Claude 3.5 Haiku")
        print(f"   Modèle : {self.model}")
        mode = (
            "RÉGÉNÉRATION COMPLÈTE"
            if regenerate_all
            else "MISE À JOUR (nouveaux uniquement)"
        )
        print(f"   Mode : {mode}")

        print("\n📊 Analyse :")
        print(f"   - Citations totales : {len(quotes)}")
        print(f"   - Haïkus existants à conserver : {skipped}")
        print(f"   - Citations à traiter : {len(quotes_to_process)}")
        print(f"   - Nombre de batchs ({self.BATCH_SIZE} citations/batch) : {batches}")

        if len(quotes_to_process) == 0:
            print("\n✅ Tous les haïkus sont déjà générés !")
            return

        # Estimation des tokens pour un batch moyen
        sample_batch = quotes_to_process[: self.BATCH_SIZE]
        tokens_est = self.estimate_batch_tokens(sample_batch)
        total_tokens = {
            "input": tokens_est["input"] * batches,
            "output": tokens_est["output"] * batches,
        }

        total_cost = self.calculate_cost(total_tokens)
        savings = self.calculate_savings(len(quotes), skipped)

        print("\n💰 Estimation des coûts :")
        print(f"   - Tokens input estimés : ~{total_tokens['input']:,}")
        print(f"   - Tokens output estimés : ~{total_tokens['output']:,}")
        print(f"   - COÛT ESTIMÉ : ${total_cost:.4f} USD")

        print("\n📈 Optimisations appliquées :")
        print(f"   ✅ Batch processing ({self.BATCH_SIZE} citations/appel)")
        print("   ✅ Génération bilingue simultanée")
        if skipped > 0:
            print(f"   ✅ Cache intelligent ({skipped} haïkus conservés)")

        print(
            f"\n💡 Économies estimées : ${savings['saved']:.4f} ({savings['percentage']:.0f}%)"
        )

    def calculate_cost(self, total_tokens: dict[str, int]) -> float:
        """Calcule le coût estimé en USD."""
        pricing = CLAUDE_PRICING.get(
            self.model, CLAUDE_PRICING["claude-3-5-haiku-20241022"]
        )

        input_cost = (total_tokens["input"] / 1_000_000) * pricing["input"]
        output_cost = (total_tokens["output"] / 1_000_000) * pricing["output"]

        return input_cost + output_cost

    def calculate_exact_cost(self, usage_metrics) -> dict[str, float]:
        """Calcule le coût exact basé sur les métriques d'utilisation réelles."""
        pricing = CLAUDE_PRICING.get(
            self.model, CLAUDE_PRICING["claude-3-5-haiku-20241022"]
        )

        input_cost = (usage_metrics.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (usage_metrics.output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
        }

    def generate_batch_haikus(self, quotes: list[Quote]) -> dict[str, dict[str, str]]:
        """Génère des haïkus pour un batch de citations."""
        if self.dry_run:
            return {
                q.id: {"fr": f"[DRY] Haïku FR {q.id}", "en": f"[DRY] Haiku EN {q.id}"}
                for q in quotes
            }

        prompt = self.create_batch_prompt(quotes)

        # Appel API avec le prompt optimisé
        response = self.api_client.client.messages.create(
            model=self.model,
            max_tokens=TOKEN_ESTIMATION["haiku_output_tokens"] * 2 * len(quotes),
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}],
        )

        # Capturer les métriques d'utilisation
        if hasattr(response, "usage"):
            self.total_metrics["input_tokens"] += response.usage.input_tokens
            self.total_metrics["output_tokens"] += response.usage.output_tokens
            self.total_metrics["batches_processed"] += 1

            # Calculer le coût de ce batch
            batch_cost = self.calculate_exact_cost(response.usage)
            self.total_metrics["total_cost"] += batch_cost["total_cost"]

        # Parser la réponse
        quote_ids = [q.id for q in quotes]
        return self.parse_batch_response(response.content[0].text, quote_ids)

    def run(self, limit: Optional[int] = None, regenerate_all: bool = False):
        """Exécute la régénération optimisée des haïkus."""
        quotes_data = CLASSIC_QUOTES[:limit] if limit else CLASSIC_QUOTES

        # Filtrer les citations à traiter
        quotes_to_process = []
        for quote_data in quotes_data:
            quote = Quote(**quote_data)
            if self.needs_regeneration(quote.id, regenerate_all):
                quotes_to_process.append(quote)

        # Afficher l'estimation
        self.display_estimation(quotes_data, regenerate_all)

        if not quotes_to_process:
            return

        # Demander confirmation
        if not self.dry_run:
            response = input("\nVoulez-vous continuer ? (o/n) : ").strip().lower()
            if response != "o":
                print("❌ Opération annulée.")
                return

        # Traiter par batchs
        print("\n🚀 Début de la génération optimisée...\n")

        success_count = 0
        error_count = 0

        for i in range(0, len(quotes_to_process), self.BATCH_SIZE):
            batch = quotes_to_process[i : i + self.BATCH_SIZE]
            batch_num = i // self.BATCH_SIZE + 1
            total_batches = (
                len(quotes_to_process) + self.BATCH_SIZE - 1
            ) // self.BATCH_SIZE

            print(
                f"[Batch {batch_num}/{total_batches}] Génération de {len(batch)} *"
                "haïkus bilingues...",
                end="",
                flush=True,
            )

            try:
                haikus = self.generate_batch_haikus(batch)

                # Sauvegarder les résultats
                for quote in batch:
                    if quote.id in haikus:
                        haiku_data = haikus[quote.id]
                        if haiku_data.get("fr") and haiku_data.get("en"):
                            if not self.dry_run:
                                self.storage.add_haiku(
                                    quote.id, haiku_data["fr"], "fr", self.model
                                )
                                self.storage.add_haiku(
                                    quote.id, haiku_data["en"], "en", self.model
                                )
                            success_count += 2  # FR + EN
                        else:
                            error_count += 2
                    else:
                        error_count += 2

                print(" ✅")

                # Pause entre les batchs
                if not self.dry_run and batch_num < total_batches:
                    time.sleep(1.0)  # 1 seconde entre les batchs

            except Exception as e:
                print(f" ❌ Erreur : {e}")
                error_count += len(batch) * 2

        # Résumé avec métriques réelles
        print("\n✨ Génération terminée !")
        print(f"   - Haïkus générés : {success_count}")
        print(f"   - Échecs : {error_count}")

        if not self.dry_run and self.total_metrics["batches_processed"] > 0:
            print("\n📊 Métriques d'utilisation réelles :")
            print(
                f"   - Tokens d'entrée totaux : {self.total_metrics['input_tokens']:,}"
            )
            print(
                f"   - Tokens de sortie totaux : {self.total_metrics['output_tokens']:,}"
            )

            print("\n💰 Coûts réels :")
            print(f"   - Coût total : ${self.total_metrics['total_cost']:.6f}")
        else:
            print(
                f"   - Économies réalisées : ~{(success_count // (self.BATCH_SIZE * 2)) * 30}% vs génération individuelle"
            )


def main():
    """Point d'entrée principal."""
    # Forcer l'encodage UTF-8 pour Windows
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Régénère les haïkus avec Claude 3.5 Haiku (version optimisée)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simule l'exécution sans appeler l'API"
    )
    parser.add_argument(
        "--limit", type=int, help="Limite le nombre de citations à traiter"
    )
    parser.add_argument(
        "--regenerate-all",
        action="store_true",
        help="Régénère TOUS les haïkus, même ceux qui existent déjà",
    )

    args = parser.parse_args()

    # Charger les variables d'environnement
    load_dotenv()

    # Vérifier la clé API
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        print("❌ Erreur : CLAUDE_API_KEY ou ANTHROPIC_API_KEY non définie dans .env")
        sys.exit(1)

    # Exécuter la régénération optimisée
    regenerator = OptimizedHaikuRegenerator(dry_run=args.dry_run)
    regenerator.run(limit=args.limit, regenerate_all=args.regenerate_all)


if __name__ == "__main__":
    main()
