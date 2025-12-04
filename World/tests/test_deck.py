import pytest

from classes.card import Card
from classes.deck import Deck


def make_cards(count: int) -> list[Card]:
    return [
        Card(
            name=f"Card {idx}",
            card_id=f"id-{idx}",
            supertype="Pokemon",
            properties=[],
            description="",
            image="",
        )
        for idx in range(count)
    ]


def test_make_deck_with_valid_size():
    cards = make_cards(Deck.DECK_SIZE)
    deck = Deck(cards)
    assert len(deck.cards) == Deck.DECK_SIZE


def test_invalid_size_raises():
    cards = make_cards(Deck.DECK_SIZE - 1)
    with pytest.raises(ValueError):
        Deck(cards)


def test_shuffle_preserves_count():
    cards = make_cards(Deck.DECK_SIZE)
    deck = Deck(cards.copy())
    deck.shuffle()
    assert len(deck.cards) == Deck.DECK_SIZE
