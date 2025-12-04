from types import SimpleNamespace

import pygame

from ui.ui_state import BattleUIState


class FakeDefinition:
    def __init__(self, name, hp=30, image=None):
        self.name = name
        self.hp = hp
        self.image = image


class FakeInstance:
    def __init__(self, name, hp=30, image=None):
        self.definition = FakeDefinition(name, hp, image=image)
        self.current_hp = hp


class FakeAPI:
    def __init__(self):
        self.active = FakeInstance("ActiveMon", 40)
        self.opp = FakeInstance("OppMon", 50)
        self.hand = [FakeInstance("Card1"), FakeInstance("Card2", image="cards/c1.png")]

    def get_active(self, state):
        return self.active

    def get_opponent_active(self, state):
        return self.opp

    def get_hand(self, state):
        return list(self.hand)


def test_ui_state_uses_accessors(monkeypatch):
    api = FakeAPI()
    monkeypatch.setattr("ui.ui_state.engine_api", api)

    state = SimpleNamespace()
    ui = BattleUIState.from_engine_state(state, actions=[{"type": "pass"}], selected_action_index=0, log_lines=[])

    assert ui.active_pokemon and ui.active_pokemon.name == "ActiveMon"
    assert ui.opponent_pokemon and ui.opponent_pokemon.name == "OppMon"
    assert ui.hand_size == 2
    assert len(ui.hand_cards) == 2
