import json
from ptcgengine.state import GameState
from ptcgengine.cards import create_card_instance
from ptcgengine.api import step, get_available_actions
from ptcgengine.actions import make_attack_action, make_pass_action

with open("ptcgengine/cards/card_db.json") as f:
    DB = json.load(f)

def _setup_state():
    state = GameState()
    p0 = create_card_instance("TestMon", DB)
    p1 = create_card_instance("TestMon", DB)
    state.players[0].active = p0
    state.players[1].active = p1
    return state

def test_energy_attach_and_attack():
    state = _setup_state()

    # Player 0 hand contains LightningEnergy
    state.players[0].hand.append(create_card_instance("LightningEnergy", DB))

    actions = get_available_actions(state, DB)
    attach = [a for a in actions if a["type"] == "attach_energy"][0]
    state, _ = step(state, attach, DB)

    atk_actions = get_available_actions(state, DB)
    atk = make_attack_action("Bonk")
    new_state, _ = step(state, atk, DB)

    assert new_state.players[1].active.current_hp == 80

def test_pass_turn():
    state = _setup_state()
    actions = get_available_actions(state, DB)
    p = [a for a in actions if a["type"] == "pass"][0]
    s2, _ = step(state, p, DB)
    assert s2.active_player == 1
