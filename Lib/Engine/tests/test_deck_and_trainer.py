from ptcgengine.deck import Deck
from ptcgengine.trainer import Trainer
from ptcgengine.card_instance import create_instance


def test_deck_round_trip():
    card = create_instance("PIKACHU-BASE")
    deck = Deck(name="Electric", cards=[card])
    dumped = deck.to_json()
    restored = Deck.from_json(dumped)
    assert restored.name == "Electric"
    assert restored.cards[0].canonical_id == card.canonical_id


def test_trainer_round_trip():
    trainer = Trainer(name="Red", deck_paths=["electric.json"], active_deck="electric.json")
    dumped = trainer.to_json()
    restored = Trainer.from_json(dumped)
    assert restored.name == "Red"
    assert restored.deck_paths == ["electric.json"]
    assert restored.active_deck == "electric.json"
