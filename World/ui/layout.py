from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import pygame


@dataclass(frozen=True)
class BattleLayout:
    """
    Computes rectangles for the battle UI, given a screen size.

    This is a debug-friendly layout with:
    - Top half: opponent + active Pokémon areas
    - Middle strip: hand
    - Bottom: action menu + event log
    """

    screen_size: Tuple[int, int]

    def compute_rects(self) -> Dict[str, pygame.Rect]:
        width, height = self.screen_size
        margin = 16
        spacing = 8

        top_height = height // 3
        bottom_height = height // 3
        middle_height = height - top_height - bottom_height - 2 * spacing

        # Top row: opponent (left) and active (right)
        top_width = (width - 3 * margin) // 2
        opponent_rect = pygame.Rect(margin, margin, top_width, top_height - margin)
        active_rect = pygame.Rect(2 * margin + top_width, margin, top_width, top_height - margin)

        # Middle: hand area across the width
        hand_rect = pygame.Rect(
            margin,
            opponent_rect.bottom + spacing,
            width - 2 * margin,
            middle_height,
        )
        hand_slots = _compute_hand_slots(hand_rect, width)

        # Bottom: actions on the left, log on the right
        bottom_top = hand_rect.bottom + spacing
        actions_width = (width - 3 * margin) // 3
        actions_rect = pygame.Rect(margin, bottom_top, actions_width, bottom_height - margin)
        log_rect = pygame.Rect(
            2 * margin + actions_width,
            bottom_top,
            width - 3 * margin - actions_width,
            bottom_height - margin,
        )

        return {
            "opponent": opponent_rect,
            "active": active_rect,
            "hand": hand_rect,
            "hand_slots": hand_slots,
            "actions": actions_rect,
            "log": log_rect,
        }


def _compute_hand_slots(hand_rect: pygame.Rect, screen_width: int) -> list[pygame.Rect]:
    max_cards_per_row = 7
    card_width = max(40, int(0.08 * screen_width))
    aspect_ratio = 0.72
    card_height = int(card_width / aspect_ratio)

    slots: list[pygame.Rect] = []
    spacing = 8

    x = hand_rect.x + spacing
    y = hand_rect.y + spacing
    cards_in_row = 0

    while y + card_height + spacing <= hand_rect.bottom and len(slots) < max_cards_per_row:
        slots.append(pygame.Rect(x, y, card_width, card_height))
        cards_in_row += 1
        if cards_in_row >= max_cards_per_row:
            break
        x += card_width + spacing
        if x + card_width + spacing > hand_rect.right:
            break

    return slots
