from dataclasses import dataclass, field
from typing import Literal

from data.constants.card_properties import ENERGY as ENERGY_CARD_PROPS
from data.constants.energy import ENERGY as ENERGY_CARD_ENERGY_TYPES
from data.constants.optional_keys import ENERGY as ENERGY_OPTIONAL_KEYS
from .card import Card


@dataclass
class Energy(Card):
    # NOTE:
    # This class is metadata-only.
    # All gameplay rules (attacks, damage, effects, evolution)
    # are implemented *exclusively* inside the functional PTCGEngine.
    energy_type: Literal["Pokemon", "Energy", "Trainer"] | str = "Energy"
    subtypes: list[str] = field(default_factory=list)

    POSSIBLE_TYPES = ENERGY_CARD_ENERGY_TYPES
    OPTIONAL_PROPERTIES = ENERGY_CARD_PROPS
    OPTIONAL_KEYS = ENERGY_OPTIONAL_KEYS
