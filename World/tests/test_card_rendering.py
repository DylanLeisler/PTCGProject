import pygame
from ui.renderer import BattleRenderer
from ui.ui_state import CardUIModel
from ui.layout import BattleLayout


def test_renderer_card_surface_smoke(tmp_path):
    pygame.init()
    screen = pygame.Surface((800, 600))
    renderer = BattleRenderer(screen)
    layout = BattleLayout(screen.get_size()).compute_rects()

    # synthetic fake sprite
    fake_img = tmp_path / "fake.png"
    surf = pygame.Surface((32, 48))
    surf.fill((255, 0, 0))
    pygame.image.save(surf, fake_img)

    model = CardUIModel(name="TestCard", sprite_path=str(fake_img))
    rect = layout["hand"]

    # Ensure no crash
    renderer._render_card(screen, model, rect)


def test_renderer_gracefully_handles_missing_asset():
    pygame.init()
    screen = pygame.Surface((800, 600))
    renderer = BattleRenderer(screen)
    model = CardUIModel(name="MissingSprite", sprite_path="does/not/exist.png")
    rect = pygame.Rect(10, 10, 120, 160)

    # Should NOT crash
    renderer._render_card(screen, model, rect)
