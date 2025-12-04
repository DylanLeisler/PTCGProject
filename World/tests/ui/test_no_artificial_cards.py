import pygame

from scenes.battle_scene import BattleScene


def test_battle_scene_does_not_inject_cards(monkeypatch):
    pygame.init()
    screen = pygame.Surface((640, 480))
    scene = BattleScene(screen, scene_manager=None)

    hand = getattr(scene.state.players[0], "hand", [])
    names = [getattr(c, "name", "") for c in hand]
    assert "Debugchu" not in names
