"""
Script de migration des haïkus existants vers le nouveau système de stockage.
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from src.donkey_quoter.data.quotes import CLASSIC_QUOTES
from src.donkey_quoter.haiku_storage import HaikuStorage
from src.donkey_quoter.models import Quote

# Convertir en objets Quote
QUOTES = [Quote(**q) for q in CLASSIC_QUOTES]

# Haïkus existants à migrer (extraits du code actuel)
EXISTING_HAIKUS = {
    "wisdom": {
        "fr": [
            "Âne sage contemple\nLes mots anciens résonnent\nVérité simple",
            "Baudet patient\nPorte la sagesse lourde\nPas lents mais sûrs",
            "Oreilles dressées\nÉcoutent la vieille voix\nSavoir ancestral",
        ],
        "en": [
            "Wise donkey reflects\nAncient words echo softly\nSimple truth endures",
            "Patient beast carries\nHeavy wisdom on his back\nSlow but steady steps",
            (
                "Ears raised high, listening\n"
                "To the old voice of knowledge\n"
                "Ancestral learning"
            ),
        ],
    },
    "humor": {
        "fr": [
            "Âne qui sourit\nSes oreilles dansent au vent\nRire contagieux",
            "Bourrique facétieux\nFait rire toute la ferme\nJoie sans prétention",
            "Pet d'âne au matin\nÉclat de rire aux champs verts\nSimple bonheur",
        ],
        "en": [
            "Smiling donkey\nEars dancing in morning breeze\nJoy without pretense",
            "Funny mule braying\nLaughter echoes through the farm\nSimple happiness",
            "Morning donkey fart\nBurst of laughter in green fields\nPure honest humor",
        ],
    },
    "work": {
        "fr": [
            "Sous le joug pesant\nL'âne avance avec courage\nDevoir accompli",
            "Fardeau sur le dos\nChemin rocailleux gravi\nForce tranquille",
            "Labeur quotidien\nÂne fidèle compagnon\nTravail noble",
        ],
        "en": [
            "Under heavy yoke\nDonkey moves with quiet strength\nDuty faithfully done",
            "Burden on the back\nRocky path climbed with courage\nPeaceful dedication",
            "Daily honest work\nFaithful donkey companion\nNoble simple labor",
        ],
    },
    "life": {
        "fr": [
            "Vivant dans l'instant\nPhilosophe mort dans l'ombre\nVie l'emporte tout",
            "Souffle de l'âne\nContre silence du sage\nExistence vraie",
            "Cœur qui bat encore\nVaut mieux qu'esprit éteint\nVie précieuse",
        ],
        "en": [
            (
                "Living in the now\n"
                "Dead philosopher in shadow\n"
                "Life conquers all thought"
            ),
            (
                "Donkey's warm breath\n"
                "Against wise man's cold silence\n"
                "Existence triumphs"
            ),
            (
                "Heart that beats today\n"
                "Beats louder than silent mind\n"
                "Life's precious rhythm"
            ),
        ],
    },
    "pride": {
        "fr": [
            "Tête d'âne fier\nQueue de cheval honteuse\nMieux vaut être soi",
            "Petit mais entier\nGrand mais incomplet souffre\nIntégrité vraie",
            "Roi sans couronne\nÂne avec sa dignité\nNoblesse du cœur",
        ],
        "en": [
            (
                "Donkey's head held high\n"
                "Horse's tail dragging in shame\n"
                "Better to be whole"
            ),
            "Small but complete soul\nLarge but broken spirit falls\nIntegrity wins",
            (
                "Crown-less but noble\n"
                "Donkey with quiet dignity\n"
                "True worth comes from within"
            ),
        ],
    },
    "patience": {
        "fr": [
            "Eau devant l'âne\nNul ne peut forcer à boire\nVolonté propre",
            "Soif seule décide\nQuand l'âne viendra s'abreuver\nSagesse d'attendre",
            "Contrainte échoue\nLibre choix seul est durable\nPatience guide",
        ],
        "en": [
            (
                "Water before donkey\n"
                "No force can make him drink deep\n"
                "Choice belongs to him"
            ),
            (
                "Only thirst decides\n"
                "When the donkey comes to drink\n"
                "Wisdom waits in patience"
            ),
            "Force always fails\nFree will alone lasts forever\nPatience teaches all",
        ],
    },
}


def find_matching_quote(theme: str) -> str:
    """Trouve une citation correspondant au thème."""
    # Mapping des thèmes vers des mots-clés
    theme_keywords = {
        "life": ["vivant", "mort", "living", "dead"],
        "pride": ["tête", "queue", "head", "tail"],
        "patience": ["boire", "eau", "drink", "water"],
        "work": ["travail", "charge", "work", "load"],
        "wisdom": ["sage", "sagesse", "wise", "wisdom"],
        "humor": ["rire", "laugh", "fun", "humor"],
    }

    keywords = theme_keywords.get(theme, [])

    # Chercher une citation qui contient ces mots-clés
    for quote in QUOTES:
        quote_text = quote.text.get("fr", "") + " " + quote.text.get("en", "")
        quote_text = quote_text.lower()

        if any(keyword in quote_text for keyword in keywords):
            return quote.id

    # Si pas de correspondance exacte, utiliser la première citation de la catégorie
    for quote in QUOTES:
        if theme == "humor" and quote.category == "humor":
            return quote.id
        elif theme in ["wisdom", "work", "patience"] and quote.category == "classic":
            return quote.id
        elif theme in ["life", "pride"] and quote.category == "personal":
            return quote.id

    # Par défaut, retourner la première citation
    return QUOTES[0].id if QUOTES else "default"


def migrate_haikus():
    """Migre les haïkus existants vers le nouveau système."""
    storage = HaikuStorage(Path("data"))

    print("Migration des haïkus existants...")

    count = 0
    for theme, languages in EXISTING_HAIKUS.items():
        # Trouver une citation correspondante
        quote_id = find_matching_quote(theme)

        for lang, haikus in languages.items():
            for haiku in haikus:
                storage.add_haiku(quote_id, haiku, lang)
                count += 1
                print(f"  - Ajouté haïku pour {quote_id} ({lang}): {haiku[:30]}...")

    print(f"\nMigration terminée : {count} haïkus migrés")

    # Afficher les statistiques
    print("\nStatistiques :")
    for quote in QUOTES:
        fr_count = storage.count_haikus(quote.id, "fr")
        en_count = storage.count_haikus(quote.id, "en")
        if fr_count > 0 or en_count > 0:
            print(f"  - {quote.id}: {fr_count} FR, {en_count} EN")


if __name__ == "__main__":
    migrate_haikus()
