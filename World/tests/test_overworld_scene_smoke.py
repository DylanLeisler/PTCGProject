import os
import pygame
import scenes.overworld_scene as ow
from scenes.overworld_scene import OverworldScene


def _init_display():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))


class DummyManager:
    pass


def _lightweight_overworld(monkeypatch):
    class DummyIngester:
        def build_index(self):
            return self

        def get_index(self):
            return {"tile": pygame.Surface((1, 1))}

    monkeypatch.setattr(ow, "Tile_Ingester", DummyIngester)

    class DummyCardManager:
        def __init__(self, *_, **__):
            self.card_index = {}

        def total_unique_cards(self):
            return 0

        def get_card_by_id(self, *_):
            return None

        def __add__(self, other):
            return self

    monkeypatch.setattr(ow, "CardManager", DummyCardManager)

    class DummyArea:
        def __init__(self, *_, **__):
            self.inanimates = []
            self._size = (10, 10)

        def get_world_size(self):
            return self._size

        def get_inanimates(self):
            return self.inanimates

    monkeypatch.setattr(ow, "Area", DummyArea)

    class DummySpriteMap:
        def __init__(self, *_, **__):
            pass

        def get_animated_sprite(self, *_, **__):
            return [[pygame.Surface((1, 1))]]

    monkeypatch.setattr(ow, "SpriteMap", DummySpriteMap)

    class DummyAnimatedSprite:
        def __init__(self, frames):
            self.rect = pygame.Rect(0, 0, 1, 1)
            self.collision_rect = self.rect.copy()
            self.sprite = pygame.Surface((1, 1))
            self.direction = "forward"
            self.position = (0, 0)

        def update(self, *_, **__):
            return None

        def get_frame(self, *_, **__):
            return self.sprite

    monkeypatch.setattr(ow, "AnimatedSprite", DummyAnimatedSprite)

    class DummyInanimate:
        def __init__(self, surface, pos):
            self.image = surface
            self.rect = surface.get_rect(topleft=pos)
            self.visual_position = pos

    monkeypatch.setattr(ow, "Inanimate", DummyInanimate)

    class DummySaveManager:
        def build_state(self, **_):
            class State:
                player_position = (0, 0)
                player_direction = "forward"
                player_name = "Player"
                area = "LAB"

            return State()

        def save(self, *_, **__):
            return "save"

        def load(self, *_, **__):
            return None

        def get_slot_metadata(self, slots):
            return {slot: {"status": "Empty"} for slot in slots}

    monkeypatch.setattr(ow, "SaveManager", DummySaveManager)
    monkeypatch.setattr(OverworldScene, "_load_overworld_sprite_assets", lambda self: {})
    monkeypatch.setattr(ow, "build_card_library", lambda *_args, **_kwargs: DummyCardManager())
    monkeypatch.setattr(ow, "load_player_collection", lambda *_args, **_kwargs: [])


def test_overworld_scene_constructs(monkeypatch):
    _init_display()
    _lightweight_overworld(monkeypatch)
    screen = pygame.display.get_surface()
    manager = DummyManager()
    scene = OverworldScene(screen, manager)
    assert scene is not None


def test_overworld_scene_update_smoke(monkeypatch):
    _init_display()
    _lightweight_overworld(monkeypatch)
    screen = pygame.display.get_surface()
    manager = DummyManager()
    scene = OverworldScene(screen, manager)
    scene.update(0.016)


def test_overworld_scene_draw_smoke(monkeypatch):
    _init_display()
    _lightweight_overworld(monkeypatch)
    screen = pygame.display.get_surface()
    manager = DummyManager()
    scene = OverworldScene(screen, manager)
    scene.draw(screen)
