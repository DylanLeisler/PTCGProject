"""
Future UI-facing support for trainer loading.

Currently: Just a stub that loads trainer + active deck via engine modules.
"""

from pathlib import Path
from ptcgengine.trainer import Trainer
from ptcgengine.deck import Deck
from ptcgengine.serialization import load_json


def load_trainer(path: str):
    data = load_json(path)
    trainer = Trainer.from_json(data)

    deck = None
    if trainer.active_deck:
        deck_data = load_json(Path(path).parent / trainer.active_deck)
        deck = Deck.from_json(deck_data)

    return trainer, deck
