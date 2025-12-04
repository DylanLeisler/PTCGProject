from dataclasses import dataclass, field

from .attack import Attack
from .card import Card
from data.constants.card_properties import POKEMON as POKEMON_CARD_PROPS
from data.constants.energy import POKEMON as POKEMON_ENERGY_TYPES
from data.constants.optional_keys import POKEMON as POKEMON_OPTIONAL_KEYS


@dataclass
class Pokemon(Card):
    # NOTE:
    # This class is metadata-only.
    # All gameplay rules (attacks, damage, effects, evolution)
    # are implemented *exclusively* inside the functional PTCGEngine.
    types: list[str] = field(default_factory=list)
    hp: str | int | None = None
    retreat: list[str] = field(default_factory=list)
    retreat_cost: int | None = None
    moves: list[Attack] = field(default_factory=list)
    evolvesFrom: str = ""
    abilities: list[dict | str] = field(default_factory=list)
    level: str = ""
    subtypes: list[str] = field(default_factory=list)
    flavorText: str = ""

    POSSIBLE_TYPES = POKEMON_ENERGY_TYPES
    POSSIBLE_PROPERTIES = POKEMON_CARD_PROPS
    OPTIONAL_KEYS = POKEMON_OPTIONAL_KEYS
