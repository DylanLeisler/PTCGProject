"""
Functions that help manage cards in PTCG-SM -- from data ingestion to data cleaning.

DO NOT add gameplay logic here. This module is metadata-only.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Literal

from classes.attack import Attack
from classes.energy import Energy
from classes.pokemon import Pokemon
from classes.trainer import Trainer


SUPERTYPE_SPELLING_VARIATIONS = {
    "Pokemon": ["PokÃ©mon", "Pokémon", "Pokemon"],
    "Energy": ["Energy"],
    "Trainer": ["Trainer"],
}
POSSIBLE_SUPERTYPES = list(SUPERTYPE_SPELLING_VARIATIONS.keys())
FIND_AND_REPLACE_COMMON_VALUES = [("PokÃ©mon", "Pokemon"), ("Pokémon", "Pokemon")]


class CardManager:
    def __init__(self, path: str | Path):
        """Requires a file path (either relative or absolute) to a JSON file containing card data."""
        self.path = Path(path)
        self.cleaned_data = self._clean_cards()
        self.cards = self.transform_card_data_types(self.cleaned_data)
        self._build_card_index()

    def __ingest_cards(func):  # type: ignore[no-redef]
        """Decorator/Context Manager that opens a JSON collection and passes it to the wrapped function."""

        def context(self, *args, **kwargs):
            with self.path.open("r", encoding="utf-8") as file:
                card_collection = json.load(file)
                return func(self, *args, card_collection=card_collection)

        return context

    @__ingest_cards
    def _extract_data_by_supertype(
        self, supertype_option: Literal["Pokemon", "Energy", "Trainer"], card_collection=None
    ):
        """Gets uncleaned card data by supertype."""
        if supertype_option not in SUPERTYPE_SPELLING_VARIATIONS:
            return []
        valid_names = SUPERTYPE_SPELLING_VARIATIONS[supertype_option]
        return [card_data for card_data in card_collection or [] if card_data.get("supertype") in valid_names]

    def change_set(self, path: str | Path):
        """Change the source file path and merge the new set."""
        self.path = Path(path)
        self.cleaned_data = self._clean_cards()
        new_cards = self.transform_card_data_types(self.cleaned_data)
        for key in self.cards.keys():
            self.cards[key] += new_cards[key]
        self._build_card_index()

    def __add__(self, value):
        combined_cards = {}
        for key in self.cards:
            combined_cards[key] = self.cards[key] + value.cards[key]
        self.cards = combined_cards
        self._build_card_index()
        return self

    def get_cards_by_supertype(self, supertype_option: Literal["Pokemon", "Energy", "Trainer"], raw=False):
        """Gets properly typed cards, filtering by supertype."""
        if raw:
            return self.cleaned_data[supertype_option]
        return self.cards[supertype_option]

    def _clean_cards(self) -> dict[str, list]:
        """Normalize keys and spelling on the raw card data."""
        cards = {
            "Pokemon": self._extract_data_by_supertype("Pokemon"),
            "Energy": self._extract_data_by_supertype("Energy"),
            "Trainer": self._extract_data_by_supertype("Trainer"),
        }
        clean_cards = {"Pokemon": [], "Energy": [], "Trainer": []}

        for supertype in POSSIBLE_SUPERTYPES:
            for unclean_card in cards[supertype]:
                keyed_data = self.generalize_spelling(dict(unclean_card), FIND_AND_REPLACE_COMMON_VALUES)
                cleaned_card = self.generalize_keys(keyed_data, globals()[supertype].OPTIONAL_KEYS)
                clean_cards[supertype].append(cleaned_card)
        return clean_cards

    def transform_card_data_types(self, cleaned_data: dict[str, list]):
        return {
            "Pokemon": self._transform_pokemon_cards(cleaned_data["Pokemon"]),
            "Energy": self._transform_energy_cards(cleaned_data["Energy"]),
            "Trainer": self._transform_trainer_cards(cleaned_data["Trainer"]),
        }

    def _transform_pokemon_cards(self, raw_data: list) -> list[Pokemon]:
        pokemon_cards: list[Pokemon] = []
        for card_data in raw_data:
            attacks_raw = card_data.get("attacks") or []
            attacks = [self._build_attack(attack) for attack in attacks_raw if isinstance(attack, dict)]
            flavor_text = card_data.get("flavorText", "") or ""
            rules_text = self._combine_rules(card_data.get("rules"))
            description = flavor_text or rules_text
            pokemon_cards.append(
                Pokemon(
                    card_data.get("name", ""),
                    card_data.get("id", ""),
                    card_data.get("supertype", ""),
                    card_data.get("subtypes") or [],
                    description,
                    self._get_image(card_data),
                    card_data.get("types") or [],
                    card_data.get("hp"),
                    card_data.get("retreatCost") or [],
                    card_data.get("convertedRetreatCost"),
                    attacks,
                    card_data.get("evolvesFrom", ""),
                    card_data.get("abilities") or [],
                    card_data.get("level", ""),
                    card_data.get("subtypes") or [],
                    flavor_text,
                )
            )
        return pokemon_cards

    def _transform_energy_cards(self, raw_data: list) -> list[Energy]:
        energy_cards: list[Energy] = []
        for card_data in raw_data:
            rules_text = self._combine_rules(card_data.get("rules"))
            base_name = card_data.get("name", "")
            energy_type = base_name.split()[0] if base_name else "Colorless"
            energy_cards.append(
                Energy(
                    card_data.get("name", ""),
                    card_data.get("id", ""),
                    card_data.get("supertype", ""),
                    card_data.get("subtypes") or [],
                    rules_text,
                    self._get_image(card_data),
                    energy_type,
                    card_data.get("subtypes") or [],
                )
            )
        return energy_cards

    def _transform_trainer_cards(self, raw_data: list) -> list[Trainer]:
        trainer_cards: list[Trainer] = []
        for card_data in raw_data:
            rules_text = self._combine_rules(card_data.get("rules"))
            subtypes = card_data.get("subtypes") or []
            trainer_cards.append(
                Trainer(
                    card_data.get("name", ""),
                    card_data.get("id", ""),
                    card_data.get("supertype", ""),
                    subtypes,
                    rules_text,
                    self._get_image(card_data),
                    subtypes,
                )
            )
        return trainer_cards

    def _build_card_index(self):
        self.card_index = {}
        for supertype_cards in self.cards.values():
            for card in supertype_cards:
                card_id = getattr(card, "card_id", None)
                if card_id:
                    self.card_index[card_id] = card

    def get_card_by_id(self, card_id: str):
        return self.card_index.get(card_id)

    def total_unique_cards(self) -> int:
        return len(self.card_index)

    @staticmethod
    def generalize_keys(unclean_data: dict, optional_keys: list) -> dict:
        for key_tuple in optional_keys:
            if key_tuple[0] not in unclean_data.keys():
                unclean_data[key_tuple[0]] = key_tuple[1]
        return unclean_data

    @staticmethod
    def generalize_spelling(card_data: dict, find_and_replace: list) -> dict:
        """Perform find/replace on all values in dictionary."""
        str_card = str(card_data)
        for word_tuple in find_and_replace:
            str_card = str_card.replace(word_tuple[0], word_tuple[1])
        return ast.literal_eval(str_card)

    @staticmethod
    def _get_image(card_data: dict) -> str:
        images = card_data.get("images") or {}
        return images.get("small", "")

    @staticmethod
    def _combine_rules(rules: list | str | None) -> str:
        if rules is None:
            return ""
        if isinstance(rules, str):
            return rules
        if isinstance(rules, list):
            return " ".join(rule for rule in rules if isinstance(rule, str))
        return ""

    @staticmethod
    def _build_attack(attack: dict | None) -> Attack:
        if not attack:
            return Attack()
        return Attack(
            name=attack.get("name", ""),
            damage=attack.get("damage", ""),
            itemized_cost=attack.get("cost", []) or [],
            total_cost=attack.get("convertedEnergyCost"),
            description=attack.get("text", ""),
        )


if __name__ == "__main__":
    exit()
