from dataclasses import dataclass, field

from data.constants.card_properties import TRAINER as TRAINER_CARD_PROPS
from data.constants.optional_keys import TRAINER as TRAINER_OPTIONAL_KEYS
from .card import Card


@dataclass
class Trainer(Card):
    # NOTE:
    # This class is metadata-only.
    # All gameplay rules (attacks, damage, effects, evolution)
    # are implemented *exclusively* inside the functional PTCGEngine.
    subtypes: list[str] = field(default_factory=list)

    OPTIONAL_PROPERTIES = TRAINER_CARD_PROPS
    OPTIONAL_KEYS = TRAINER_OPTIONAL_KEYS
