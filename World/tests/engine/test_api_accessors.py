from ptcgengine import api
from ptcgengine.cards import PokemonCard
from ptcgengine.state import GameState


def _make_state():
    state = GameState()
    p0 = PokemonCard(card_id="A", supertype="pokemon", name="Alpha", hp=50, current_hp=50, types=["normal"])
    p1 = PokemonCard(card_id="B", supertype="pokemon", name="Beta", hp=40, current_hp=40, types=["normal"])
    state.players[0].active = p0
    state.players[1].active = p1
    state.players[0].hand = [p0]
    return state


def test_get_active_and_opponent():
    state = _make_state()
    active = api.get_active(state)
    opp = api.get_opponent_active(state)
    assert active is not None and active.definition.name == "Alpha"
    assert opp is not None and opp.definition.name == "Beta"


def test_get_hand_returns_instances():
    state = _make_state()
    hand = api.get_hand(state)
    assert len(hand) == 1
    assert hand[0].definition.name == "Alpha"
