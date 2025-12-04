from __future__ import annotations

from typing import Dict

import pygame

from .ui_state import BattleUIState
from .widgets import draw_highlight, draw_panel, draw_text_lines


class BattleRenderer:
    """
    Debug-first renderer for the BattleUIState.

    Uses a monospace font for alignment and clarity.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        # Monospace preference; fall back to default if unavailable.
        try:
            self.font = pygame.font.SysFont("consolas", 16)
        except Exception:
            self.font = pygame.font.Font(None, 16)
        self._sprite_cache: dict[str, pygame.Surface] = {}
        self._placeholder = self._make_placeholder()

    def _make_placeholder(self) -> pygame.Surface:
        surf = pygame.Surface((64, 92), pygame.SRCALPHA)
        surf.fill((40, 40, 40))
        pygame.draw.rect(surf, (120, 120, 120), surf.get_rect(), 2)
        return surf

    def render(self, ui: BattleUIState, rects: Dict[str, pygame.Rect]) -> None:
        self.ui_state = ui  # cache for helper access
        self.screen.fill((0, 0, 0))

        # Opponent and active Pokémon panels
        self._render_pokemon_panel(rects["opponent"], ui.opponent_pokemon, "Opponent")
        self._render_pokemon_panel(rects["active"], ui.active_pokemon, "Active")

        # Hand (just show count for now)
        self._render_hand(rects.get("hand"), rects.get("hand_slots", []), ui)

        # Actions
        self._render_actions(rects["actions"], ui.actions, ui.selected_action_index)

        # Log
        self._render_log(rects["log"], ui.log_lines)

    def _render_pokemon_panel(self, rect, pkm, title: str) -> None:
        lines = [title]
        if pkm is None:
            lines.append("(none)")
        else:
            hp_str = "?"
            if pkm.current_hp is not None and pkm.max_hp is not None:
                hp_str = f"{pkm.current_hp}/{pkm.max_hp}"
            elif pkm.current_hp is not None:
                hp_str = str(pkm.current_hp)

            lines.append(pkm.name)
            lines.append(f"HP: {hp_str}")

        draw_panel(self.screen, rect)
        draw_text_lines(self.screen, rect, self.font, lines)

    def _render_hand(self, rect, slots, ui_state: BattleUIState) -> None:
        if rect is None:
            return

        draw_panel(self.screen, rect)

        models = list(ui_state.hand_cards) if ui_state.hand_cards else []
        if not models and ui_state.hand_size > 0:
            for i in range(ui_state.hand_size):
                models.append(type("AnonCard", (), {"name": f"Card {i+1}", "sprite_path": None})())

        if ui_state.hand_size == 0 and not models:
            draw_text_lines(self.screen, rect, self.font, ["Hand: empty"])
            return

        self._render_hand_cards(rect, models, slots)

    def _render_actions(self, rect, actions, selected_idx: int) -> None:
        draw_panel(self.screen, rect)
        if not actions:
            draw_text_lines(self.screen, rect, self.font, ["No actions"])
            return

        x = rect.x + 4
        y = rect.y + 4
        max_y = rect.bottom - 4
        for idx, label in enumerate(actions):
            if y >= max_y:
                break
            surf = self.font.render(str(label), True, (230, 230, 230))
            pos = (x, y)
            self.screen.blit(surf, pos)
            if idx == selected_idx:
                highlight_rect = pygame.Rect(pos[0] - 2, pos[1] - 2, surf.get_width() + 4, surf.get_height() + 4)
                draw_highlight(self.screen, highlight_rect)
            y += surf.get_height() + 4

    def _render_log(self, rect, lines) -> None:
        draw_panel(self.screen, rect)
        max_lines = 50
        subset = list(lines)[-max_lines:]
        draw_text_lines(self.screen, rect, self.font, subset)

    def _load_sprite(self, path: str) -> pygame.Surface:
        if path in self._sprite_cache:
            return self._sprite_cache[path]
        surf = None
        try:
            surf = pygame.image.load(path).convert_alpha()
        except Exception:
            surf = None

        if surf is None:
            return self._placeholder

        self._sprite_cache[path] = surf
        return surf

    def _render_card(self, surface: pygame.Surface, model, rect: pygame.Rect) -> None:
        draw_panel(surface, rect)

        sprite_path = getattr(model, "sprite_path", None)
        if getattr(model, "is_hidden", False):
            self._render_card_back(surface, rect)
            return

        sprite = self._placeholder
        if sprite_path:
            sprite = self._load_sprite(sprite_path)

        margin = 6
        text = self.font.render(str(getattr(model, "name", "Card")), True, (240, 240, 240))
        available_height = rect.height - text.get_height() - margin * 3
        available_width = rect.width - margin * 2

        if sprite.get_width() > 0 and sprite.get_height() > 0:
            scale = min(available_width / sprite.get_width(), available_height / sprite.get_height())
            scale = max(scale, 0.1)
            new_size = (
                max(1, int(sprite.get_width() * scale)),
                max(1, int(sprite.get_height() * scale)),
            )
            scaled = pygame.transform.smoothscale(sprite, new_size)
        else:
            scaled = sprite

        sprite_x = rect.x + (rect.width - scaled.get_width()) // 2
        sprite_y = rect.y + margin
        surface.blit(scaled, (sprite_x, sprite_y))

        text_pos = (rect.x + (rect.width - text.get_width()) // 2, rect.bottom - text.get_height() - margin)
        surface.blit(text, text_pos)

    def _render_card_back(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        draw_panel(surface, rect)
        sprite = self._placeholder
        back_path = Path(__file__).parent.parent / "assets" / "ui" / "card_back.png"
        if back_path.exists():
            try:
                sprite = self._load_sprite(str(back_path))
            except Exception:
                sprite = self._placeholder

        margin = 6
        if sprite.get_width() > 0 and sprite.get_height() > 0:
            scale = min((rect.width - margin * 2) / sprite.get_width(), (rect.height - margin * 2) / sprite.get_height())
            scale = max(scale, 0.1)
            new_size = (
                max(1, int(sprite.get_width() * scale)),
                max(1, int(sprite.get_height() * scale)),
            )
            sprite = pygame.transform.smoothscale(sprite, new_size)

        pos = (rect.x + (rect.width - sprite.get_width()) // 2, rect.y + (rect.height - sprite.get_height()) // 2)
        surface.blit(sprite, pos)

    def _render_hand_cards(self, hand_rect, models, slots):
        resolved_slots = slots if slots else [hand_rect]
        for idx, model in enumerate(models):
            if idx >= len(resolved_slots):
                break
            self._render_card(self.screen, model, resolved_slots[idx])

    def _render_opponent_hand(self, rect, ui: BattleUIState) -> None:
        if rect is None or ui.opponent_hand is None or ui.opponent_hand.count == 0:
            return

        count = ui.opponent_hand.count
        slots = count if count <= 7 else 7
        spacing = 30
        width = 50
        height = 70

        for i in range(slots):
            slot = pygame.Rect(rect.x + 10 + i * spacing, rect.y - height - 12, width, height)
            self._render_card_back(self.screen, slot)
