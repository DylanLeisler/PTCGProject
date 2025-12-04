import os
import pygame
from types import SimpleNamespace

from scenes.overworld_scene import OverworldScene
from scenes.battle_scene import BattleScene


class DummySceneManager:
    def __init__(self):
        self.stack = []

    def push(self, scene):
        self.stack.append(scene)

    def pop(self):
        if self.stack:
            self.stack.pop()


def test_no_scene_pushed_when_trigger_false(monkeypatch):
    """Tests that once _can_trigger_battle has logic, the guard works."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))

    manager = DummySceneManager()
    screen = pygame.Surface((640, 480))
    scene = OverworldScene(screen, scene_manager=manager)

    # Force trigger to return False
    monkeypatch.setattr(scene, "_can_trigger_battle", lambda: False)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
    scene.handle_event(event)

    assert not manager.stack, "BattleScene should NOT be pushed when trigger guard is false."


def test_initial_state_is_forwarded(monkeypatch):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))

    # Fake engine API returning known sentinel
    fake_state = SimpleNamespace(tag="unit_test_state")

    class FakeAPI:
        @staticmethod
        def initial_state():
            return fake_state

        @staticmethod
        def get_available_actions(state):
            return [{"type": "pass"}]

        @staticmethod
        def step(state, action):
            return state

    from scenes import battle_scene as bs
    monkeypatch.setattr(bs, "api", FakeAPI)

    manager = DummySceneManager()
    screen = pygame.Surface((640, 480))
    scene = OverworldScene(screen, scene_manager=manager)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
    scene.handle_event(event)

    assert manager.stack, "Expected BattleScene to be pushed."
    assert manager.stack[-1].state is fake_state, "Initial state must be forwarded to BattleScene."


def test_overworld_unchanged_after_push(monkeypatch):
    """Ensures immutable scene model: pushing next scene must not alter overworld."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))

    manager = DummySceneManager()
    screen = pygame.Surface((640, 480))
    scene = OverworldScene(screen, scene_manager=manager)

    # Snapshot attributes before
    before = dict(vars(scene))

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
    scene.handle_event(event)

    after = dict(vars(scene))

    # Remove scene_manager and screen (those are expected shared references)
    before.pop("scene_manager", None)
    before.pop("screen", None)
    after.pop("scene_manager", None)
    after.pop("screen", None)

    assert before == after, "OverworldScene must not mutate itself due to battle transition."
