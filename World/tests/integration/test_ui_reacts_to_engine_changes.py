from ptcgengine import api
from ptcgengine.cards import PokemonCard
from ptcgengine.state import GameState
from ui.ui_state import BattleUIState


def _setup_state():
    state = GameState()
    p0 = PokemonCard(card_id="A", supertype="pokemon", name="Alpha", hp=50, current_hp=50, types=["normal"])
    p1 = PokemonCard(card_id="B", supertype="pokemon", name="Beta", hp=40, current_hp=40, types=["normal"])
    state.players[0].active = p0
    state.players[1].active = p1
    state.players[0].hand = [p0]
    return state


def test_ui_updates_after_action():
    state = _setup_state()
    actions = api.get_available_actions(state, None)
    if actions:
        state, _ = api.step(state, actions[0], None)
    ui = BattleUIState.from_engine_state(state, actions, selected_action_index=0, log_lines=[])

    assert ui.active_pokemon is not None
    assert ui.opponent_pokemon is not None
    assert ui.hand_size == len(api.get_hand(state))
