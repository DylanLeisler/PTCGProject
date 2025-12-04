import os
import pygame
from scenes.title_scene import TitleScene


class DummyOverworld:
    def __init__(self, *args, **kwargs):
        pass


class DummyManager:
    def __init__(self):
        self.replaced_with = None

    def replace(self, scene):
        self.replaced_with = scene


def _init_display():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))


def test_title_scene_transition():
    _init_display()
    screen = pygame.display.get_surface()
    manager = DummyManager()
    scene = TitleScene(screen, manager)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x)
    # Avoid expensive overworld construction during this test.
    import scenes.title_scene as ts
    original_overworld = ts.OverworldScene
    ts.OverworldScene = DummyOverworld
    try:
        scene.handle_event(event)
    finally:
        ts.OverworldScene = original_overworld

    assert isinstance(manager.replaced_with, DummyOverworld)


def test_title_scene_ignore_other_keys():
    _init_display()
    screen = pygame.display.get_surface()
    manager = DummyManager()
    scene = TitleScene(screen, manager)

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    scene.handle_event(event)

    assert manager.replaced_with is None
