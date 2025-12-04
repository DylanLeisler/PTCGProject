import os
import pygame

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


def test_pressing_interact_pushes_battle_scene(monkeypatch):
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))  # Required for some pygame builds

    manager = DummySceneManager()
    screen = pygame.Surface((640, 480))

    scene = OverworldScene(screen, scene_manager=manager)

    # Simulate pressing E
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)
    scene.handle_event(event)

    assert manager.stack, "Expected a scene to be pushed after pressing interact key."
    assert isinstance(manager.stack[-1], BattleScene), "Pushed scene must be BattleScene."
