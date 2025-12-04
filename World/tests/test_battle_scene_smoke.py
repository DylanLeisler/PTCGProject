import os
import pygame
from scenes.battle_scene import BattleScene


def _init_display():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))


def test_battle_scene_constructs():
    _init_display()
    screen = pygame.display.get_surface()
    scene = BattleScene(screen)
    assert scene is not None


def test_battle_scene_draw_smoke():
    _init_display()
    screen = pygame.display.get_surface()
    scene = BattleScene(screen)
    scene.draw(screen)
