import os
import pygame
from types import SimpleNamespace

import scenes.battle_scene as bs


class DummyAPI:
    def __init__(self):
        self.initial_state_called = False
        self.step_calls: list[tuple[object, dict]] = []
        self._actions = [
            {"type": "pass", "label": "Pass"},
            {"type": "attack", "label": "Attack 1"},
        ]

    def initial_state(self):
        self.initial_state_called = True
        return SimpleNamespace(tag="dummy_state")

    def get_available_actions(self, state):
        # we ignore state contents here; just return a static set
        return list(self._actions)

    def step(self, state, action):
        self.step_calls.append((state, action))
        return SimpleNamespace(tag="next_state")


class DummyManager:
    def __init__(self):
        self.popped = False

    def pop(self):
        self.popped = True


def test_battle_scene_applies_action(monkeypatch):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    screen = pygame.Surface((640, 480))

    dummy_api = DummyAPI()
    # Replace the 'api' object inside scenes.battle_scene with our dummy
    monkeypatch.setattr(bs, "api", dummy_api, raising=False)

    scene = bs.BattleScene(screen, scene_manager=None)

    # Actions should have been loaded from dummy_api
    assert scene.actions
    assert len(scene.actions) == 2

    # Select the second action ("attack")
    scene.selected_action_index = 1

    # Simulate pressing ENTER
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    scene.handle_event(event)

    # step() must have been called at least once
    assert dummy_api.step_calls, "Expected api.step to be called"

    _state, action = dummy_api.step_calls[-1]
    assert action["type"] == "attack"

    # Log should contain at least one entry reflecting the chosen action
    assert scene.log, "Battle log should record applied actions"
    assert "attack" in scene.log[-1].lower()


def test_battle_scene_exit_on_escape(monkeypatch):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    screen = pygame.Surface((640, 480))

    dummy_api = DummyAPI()
    monkeypatch.setattr(bs, "api", dummy_api, raising=False)

    manager = DummyManager()
    scene = bs.BattleScene(screen, scene_manager=manager)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    scene.handle_event(event)

    assert manager.popped, "Escape key should trigger scene_manager.pop()"
