import pygame
from types import SimpleNamespace

from scenes.battle_scene import BattleScene


class FakeAPI:
    def __init__(self):
        self._actions = [{"type": "attack"}]

    def initial_state(self):
        return SimpleNamespace(event_log=[])

    def get_available_actions(self, state):
        return list(self._actions)

    def step(self, state, action):
        # Fake structured event
        ev = SimpleNamespace(type="attack", payload={"source": "Pikachu", "target": "Bulbasaur", "damage": 30})
        return SimpleNamespace(event_log=state.event_log + [ev]), [ev]


def test_event_logging(monkeypatch):
    pygame.init()
    screen = pygame.Surface((600, 400))
    monkeypatch.setattr("scenes.battle_scene.api", FakeAPI())

    scene = BattleScene(screen, None)
    scene.selected_action_index = 0

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    scene.handle_event(event)

    assert scene.log, "UI log should contain rendered messages"
    assert "Pikachu" in scene.log[-1]
