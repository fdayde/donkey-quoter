"""
Module de génération de haïkus.
"""
import random
import time
from datetime import datetime
from typing import Dict, Optional

import streamlit as st

from .models import Quote


class HaikuGenerator:
    """Générateur de haïkus basé sur les citations."""

    HAIKU_COLLECTIONS = {
        "fr": {
            "wisdom": [
                "Âne sage contemple\nLes mots anciens résonnent\nVérité simple",
                "Baudet patient\nPorte la sagesse lourde\nPas lents mais sûrs",
                "Oreilles dressées\nÉcoutent la vieille voix\nSavoir ancestral",
            ],
            "humor": [
                "Âne qui sourit\nSes oreilles dansent au vent\nRire contagieux",
                "Bourrique facétieux\nFait rire toute la ferme\nJoie sans prétention",
                "Pet d'âne au matin\nÉclat de rire aux champs verts\nSimple bonheur",
            ],
            "work": [
                "Sous le joug pesant\nL'âne avance avec courage\nDevoir accompli",
                "Fardeau sur le dos\nChemin rocailleux gravi\nForce tranquille",
                "Labeur quotidien\nÂne fidèle compagnon\nTravail noble",
            ],
            "life": [
                "Vivant dans l'instant\nPhilosophe mort dans l'ombre\nVie l'emporte tout",
                "Souffle de l'âne\nContre silence du sage\nExistence vraie",
                "Cœur qui bat encore\nVaut mieux qu'esprit éteint\nVie précieuse",
            ],
            "pride": [
                "Tête d'âne fier\nQueue de cheval honteuse\nMieux vaut être soi",
                "Petit mais entier\nGrand mais incomplet souffre\nIntégrité vraie",
                "Roi sans couronne\nÂne avec sa dignité\nNoblesse du cœur",
            ],
            "patience": [
                "Eau devant l'âne\nNul ne peut forcer à boire\nVolonté propre",
                "Soif seule décide\nQuand l'âne viendra s'abreuver\nSagesse d'attendre",
                "Contrainte échoue\nLibre choix seul est durable\nPatience guide",
            ],
        },
        "en": {
            "wisdom": [
                "Wise donkey reflects\nAncient words echo softly\nSimple truth endures",
                "Patient beast carries\nHeavy wisdom on his back\nSlow but steady steps",
                "Ears raised high, listening\nTo the old voice of knowledge\nAncestral learning",
            ],
            "humor": [
                "Smiling donkey\nEars dancing in morning breeze\nJoy without pretense",
                "Funny mule braying\nLaughter echoes through the farm\nSimple happiness",
                "Morning donkey fart\nBurst of laughter in green fields\nPure honest humor",
            ],
            "work": [
                "Under heavy yoke\nDonkey moves with quiet strength\nDuty faithfully done",
                "Burden on the back\nRocky path climbed with courage\nPeaceful dedication",
                "Daily honest work\nFaithful donkey companion\nNoble simple labor",
            ],
            "life": [
                "Living in the now\nDead philosopher in shadow\nLife conquers all thought",
                "Donkey's warm breath\nAgainst wise man's cold silence\nExistence triumphs",
                "Heart that beats today\nBeats louder than silent mind\nLife's precious rhythm",
            ],
            "pride": [
                "Donkey's head held high\nHorse's tail dragging in shame\nBetter to be whole",
                "Small but complete soul\nLarge but broken spirit falls\nIntegrity wins",
                "Crown-less but noble\nDonkey with quiet dignity\nTrue worth comes from within",
            ],
            "patience": [
                "Water before donkey\nNo force can make him drink deep\nChoice belongs to him",
                "Only thirst decides\nWhen the donkey comes to drink\nWisdom waits in patience",
                "Force always fails\nFree will alone lasts forever\nPatience teaches all",
            ],
        },
    }

    def __init__(self):
        """Initialise le générateur de haïkus."""
        pass

    def get_theme_from_quote(
        self, text: str, author: str, category: str
    ) -> str:
        """Détermine le thème approprié basé sur la citation."""
        if category == "humor":
            return "humor"

        text_lower = text.lower()
        keywords = {
            "life": ["vivant", "mort", "living", "dead"],
            "pride": ["tête", "queue", "head", "tail"],
            "patience": ["boire", "eau", "drink", "water"],
            "work": ["travail", "charge", "work", "load"],
            "wisdom": ["sage", "sagesse", "wise", "wisdom"],
        }

        for theme, words in keywords.items():
            if any(word in text_lower for word in words):
                return theme

        return "wisdom"

    def generate_from_quote(
        self, quote: Quote, language: str
    ) -> Optional[Quote]:
        """Génère un haïku basé sur une citation."""
        # Simuler le temps de génération
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.015)
            progress_bar.progress(i + 1)
        progress_bar.empty()

        # Obtenir le texte dans la langue courante
        text = quote.text.get(language, quote.text.get("fr", ""))
        author = quote.author.get(language, quote.author.get("fr", ""))

        # Déterminer le thème
        theme = self.get_theme_from_quote(text, author, quote.category)

        # Sélectionner un haïku aléatoire
        haiku_list = self.HAIKU_COLLECTIONS.get(language, {}).get(
            theme, self.HAIKU_COLLECTIONS[language]["wisdom"]
        )
        selected_haiku = random.choice(haiku_list)

        # Créer le poème
        poem = Quote(
            id=f"poem_{int(datetime.now().timestamp())}",
            text={
                language: selected_haiku,
                "fr" if language == "en" else "en": selected_haiku,
            },
            author={"fr": "Maître du Haïku", "en": "Haiku Master"},
            category="poem",
            type="generated",
        )

        return poem