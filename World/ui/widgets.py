from __future__ import annotations

from typing import Iterable, Tuple

import pygame


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    bg_color: Tuple[int, int, int] = (20, 20, 20),
    border_color: Tuple[int, int, int] = (200, 200, 200),
    border_width: int = 1,
) -> None:
    pygame.draw.rect(surface, bg_color, rect)
    pygame.draw.rect(surface, border_color, rect, border_width)


def draw_text_lines(
    surface: pygame.Surface,
    rect: pygame.Rect,
    font: pygame.font.Font,
    lines: Iterable[str],
    color: Tuple[int, int, int] = (230, 230, 230),
    line_spacing: int = 2,
) -> None:
    x = rect.x + 4
    y = rect.y + 4
    max_y = rect.bottom - 4
    for line in lines:
        if y >= max_y:
            break
        surf = font.render(str(line), True, color)
        surface.blit(surf, (x, y))
        y += surf.get_height() + line_spacing


def draw_highlight(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: Tuple[int, int, int] = (255, 255, 0),
    width: int = 2,
) -> None:
    pygame.draw.rect(surface, color, rect, width)
