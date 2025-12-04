from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence
import textwrap

import pygame


@dataclass(frozen=True)
class MenuOption:
    label: str
    action: str


class PauseMenu:
    """Simple pause menu overlay that can be toggled with the Start button."""

    def __init__(
        self,
        screen: pygame.Surface,
        title: str = "PAUSE",
        options: Sequence[MenuOption] | None = None,
    ) -> None:
        self.screen = screen
        self.title = title
        self.options = list(
            options
            or [
                MenuOption("Resume", "resume"),
                MenuOption("Deck", "deck"),
                MenuOption("Save", "save"),
                MenuOption("Load", "load"),
                MenuOption("Quit", "quit"),
            ]
        )
        if not self.options:
            raise ValueError("PauseMenu requires at least one menu option.")

        self.visible = False
        self.selected_index = 0
        self.overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.panel_rect = pygame.Rect(0, 0, int(self.screen.get_width() * 0.5), int(self.screen.get_height() * 0.6))
        self.panel_rect.center = self.screen.get_rect().center

        # Fonts - default pygame font is fine for now.
        self.title_font = pygame.font.Font(None, 48)
        self.option_font = pygame.font.Font(None, 32)

        # Colors
        self.overlay_color = (0, 0, 0, 180)
        self.panel_color = (26, 26, 42, 225)
        self.border_color = (255, 255, 255)
        self.inactive_color = (180, 180, 200)
        self.active_color = (255, 255, 255)

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def toggle(self) -> None:
        self.visible = not self.visible

    def move_selection(self, delta: int) -> None:
        self.selected_index = (self.selected_index + delta) % len(self.options)

    def handle_key(self, key: int) -> str | None:
        if key in (pygame.K_UP, pygame.K_w):
            self.move_selection(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.move_selection(1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.options[self.selected_index].action
        elif key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.hide()
            return "resume"
        return None

    def draw(self) -> None:
        if not self.visible:
            return

        # Dimmed background
        self.overlay.fill(self.overlay_color)
        self.screen.blit(self.overlay, (0, 0))

        # Panel
        panel_surface = pygame.Surface(self.panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill(self.panel_color)
        pygame.draw.rect(panel_surface, self.border_color, panel_surface.get_rect(), 2)
        self.screen.blit(panel_surface, self.panel_rect.topleft)

        # Title
        title_surface = self.title_font.render(self.title, True, self.active_color)
        title_rect = title_surface.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 40))
        self.screen.blit(title_surface, title_rect)

        # Options
        option_start_y = title_rect.bottom + 20
        line_height = self.option_font.get_height() + 10
        for idx, option in enumerate(self.options):
            is_selected = idx == self.selected_index
            color = self.active_color if is_selected else self.inactive_color
            label_surface = self.option_font.render(option.label, True, color)
            label_rect = label_surface.get_rect()
            label_rect.centerx = self.panel_rect.centerx
            label_rect.y = option_start_y + idx * line_height

            if is_selected:
                highlight_rect = label_rect.inflate(40, 10)
                pygame.draw.rect(self.screen, self.active_color, highlight_rect, 2)

            self.screen.blit(label_surface, label_rect)


class DeckMenu:
    """Displays the player's current collection with a detail pane."""

    def __init__(self, screen: pygame.Surface, title: str = "DECK") -> None:
        self.screen = screen
        self.title = title
        self.visible = False
        self.overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.title_font = pygame.font.Font(None, 60)
        self.body_font = pygame.font.Font(None, 32)
        self.detail_font = pygame.font.Font(None, 26)
        self.overlay_color = (6, 10, 40, 230)
        self.accent_color = (255, 255, 255)
        self.sub_color = (200, 200, 210)
        self.entries: list[dict[str, Any]] = []
        self.summary: dict[str, int] = {}
        self.scroll_offset = 0
        self.entries_per_page = 6
        self.selected_index = 0

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def handle_key(self, key: int) -> str | None:
        total_entries = len(self.entries)
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_RETURN, pygame.K_SPACE):
            return "back"
        if total_entries == 0:
            return None

        if key in (pygame.K_UP, pygame.K_w):
            self.selected_index = (self.selected_index - 1) % total_entries
            self._ensure_selection_visible()
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected_index = (self.selected_index + 1) % total_entries
            self._ensure_selection_visible()
        elif key == pygame.K_PAGEUP:
            self.selected_index = max(0, self.selected_index - self.entries_per_page)
            self._ensure_selection_visible(force_top=True)
        elif key == pygame.K_PAGEDOWN:
            self.selected_index = min(total_entries - 1, self.selected_index + self.entries_per_page)
            self._ensure_selection_visible(force_bottom=True)
        elif key == pygame.K_HOME:
            self.selected_index = 0
            self._ensure_selection_visible(force_top=True)
        elif key == pygame.K_END:
            self.selected_index = total_entries - 1
            self._ensure_selection_visible(force_bottom=True)
        return None

    def set_deck_data(self, entries: list[dict[str, Any]] | None, summary: dict[str, int] | None) -> None:
        self.entries = entries or []
        self.summary = summary or {}
        self.scroll_offset = 0
        self.selected_index = 0

    def draw(self) -> None:
        if not self.visible:
            return
        self.overlay.fill(self.overlay_color)
        self.screen.blit(self.overlay, (0, 0))

        title_surface = self.title_font.render(self.title, True, self.accent_color)
        title_rect = title_surface.get_rect(center=(self.screen.get_rect().centerx, 80))
        self.screen.blit(title_surface, title_rect)

        summary_lines: list[str] = []
        for key in ("Pokemon", "Trainer", "Energy", "Unknown"):
            if (value := self.summary.get(key)):
                summary_lines.append(f"{key}: {value}")
        if "Total" in self.summary:
            summary_lines.append(f"Owned: {self.summary['Total']}")
        if "Available" in self.summary and self.summary["Available"]:
            summary_lines.append(f"Available: {self.summary['Available']}")

        summary_y = title_rect.bottom + 10
        for line in summary_lines:
            text_surface = self.body_font.render(line, True, self.sub_color)
            text_rect = text_surface.get_rect(center=(self.screen.get_rect().centerx, summary_y))
            self.screen.blit(text_surface, text_rect)
            summary_y += self.body_font.get_height() + 5

        list_start_y = summary_y + 20
        row_height = self.detail_font.get_height() + 10

        if not self.entries:
            empty_surface = self.body_font.render("No cards owned yet.", True, self.sub_color)
            empty_rect = empty_surface.get_rect(center=(self.screen.get_rect().centerx, list_start_y + 40))
            self.screen.blit(empty_surface, empty_rect)
            return

        for idx in range(self.entries_per_page):
            entry_index = self.scroll_offset + idx
            if entry_index >= len(self.entries):
                break
            entry = self.entries[entry_index]
            line = f"{entry.get('supertype', 'Unknown'):>8}  |  {entry.get('name', 'Unknown')} ({entry.get('id', '???')})"
            entry_surface = self.detail_font.render(line, True, self.accent_color)
            entry_rect = entry_surface.get_rect()
            entry_rect.centerx = self.screen.get_rect().centerx
            entry_rect.y = list_start_y + idx * row_height
            if entry_index == self.selected_index:
                highlight_rect = entry_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, self.accent_color, highlight_rect, 2)
            self.screen.blit(entry_surface, entry_rect)

        start = self.scroll_offset + 1
        end = min(len(self.entries), self.scroll_offset + self.entries_per_page)
        total = len(self.entries)
        footer_text = f"{start}-{end} / {total}"
        footer_surface = self.detail_font.render(footer_text, True, self.sub_color)
        footer_rect = footer_surface.get_rect()
        footer_rect.centerx = self.screen.get_rect().centerx
        footer_rect.y = self.screen.get_height() - footer_rect.height - 30
        self.screen.blit(footer_surface, footer_rect)

        selected_entry = self.entries[self.selected_index]
        self._draw_detail_panel(selected_entry)

    def _ensure_selection_visible(self, force_top: bool = False, force_bottom: bool = False) -> None:
        if force_top:
            self.scroll_offset = self.selected_index
        elif force_bottom:
            self.scroll_offset = self.selected_index - self.entries_per_page + 1

        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.entries_per_page:
            self.scroll_offset = self.selected_index - self.entries_per_page + 1
        max_offset = max(0, len(self.entries) - self.entries_per_page)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))

    def _draw_detail_panel(self, entry: dict[str, Any]) -> None:
        panel_width = self.screen.get_width() - 160
        panel_height = 190
        panel_rect = pygame.Rect(80, self.screen.get_height() - panel_height - 60, panel_width, panel_height)
        panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill((12, 20, 55, 220))
        pygame.draw.rect(panel_surface, self.accent_color, panel_surface.get_rect(), 2)

        card = entry.get("card")
        supertype = entry.get("supertype", "Unknown")
        if card:
            supertype = getattr(card, "supertype", supertype)

        info_lines = [
            f"Name: {entry.get('name', 'Unknown')}",
            f"Card ID: {entry.get('id', '???')}",
            f"Supertype: {supertype}",
        ]
        if card:
            if hasattr(card, "energy_type"):
                info_lines.append(f"Energy: {getattr(card, 'energy_type')}")
            card_props = getattr(card, "properties", None)
            if card_props:
                info_lines.append(f"Properties: {', '.join(card_props)}")
            evolves_from = getattr(card, "evolvesFrom", "")
            if evolves_from:
                info_lines.append(f"Evolves From: {evolves_from}")

        description = ""
        if card:
            description = getattr(card, "description", "") or ""
        elif entry.get("description"):
            description = entry["description"]

        text_y = 15
        for line in info_lines:
            text_surface = self.detail_font.render(line, True, self.accent_color)
            panel_surface.blit(text_surface, (20, text_y))
            text_y += self.detail_font.get_height() + 4

        if card and hasattr(card, "moves") and getattr(card, "moves"):
            moves = getattr(card, "moves")
            move_names = ", ".join(move.name for move in moves if getattr(move, "name", None))
            if move_names:
                move_line = self.detail_font.render(f"Moves: {move_names}", True, self.accent_color)
                panel_surface.blit(move_line, (20, text_y))
                text_y += self.detail_font.get_height() + 6

        if description:
            wrapped = textwrap.wrap(description, width=80)
            for line in wrapped[:4]:
                text_surface = self.detail_font.render(line, True, self.sub_color)
                panel_surface.blit(text_surface, (20, text_y))
                text_y += self.detail_font.get_height() + 2

        self.screen.blit(panel_surface, panel_rect.topleft)


class ConfirmDialog:
    """Simple yes/no confirmation dialog that sits on top of other overlays."""

    def __init__(
        self,
        screen: pygame.Surface,
        message: str = "Exit the game?",
        options: Sequence[MenuOption] | None = None,
    ) -> None:
        self.screen = screen
        self.message = message
        self.options = list(options or [MenuOption("Yes", "yes"), MenuOption("No", "no")])
        self.visible = False
        self.selected_index = 0
        self.overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.overlay_color = (0, 0, 0, 100)
        self.panel_rect = pygame.Rect(0, 0, int(self.screen.get_width() * 0.4), int(self.screen.get_height() * 0.3))
        self.panel_rect.center = self.screen.get_rect().center
        self.panel_color = (50, 20, 20, 240)
        self.border_color = (255, 255, 255)
        self.message_font = pygame.font.Font(None, 40)
        self.option_font = pygame.font.Font(None, 32)

    def show(self, message: str | None = None) -> None:
        if message:
            self.message = message
        self.visible = True
        self.selected_index = 0

    def hide(self) -> None:
        self.visible = False

    def move_selection(self, delta: int) -> None:
        self.selected_index = (self.selected_index + delta) % len(self.options)

    def handle_key(self, key: int) -> str | None:
        if key in (pygame.K_LEFT, pygame.K_a):
            self.move_selection(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.move_selection(1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.options[self.selected_index].action
        elif key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.hide()
            return "no"
        return None

    def draw(self) -> None:
        if not self.visible:
            return

        self.overlay.fill(self.overlay_color)
        self.screen.blit(self.overlay, (0, 0))

        panel_surface = pygame.Surface(self.panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill(self.panel_color)
        pygame.draw.rect(panel_surface, self.border_color, panel_surface.get_rect(), 2)
        self.screen.blit(panel_surface, self.panel_rect.topleft)

        message_surface = self.message_font.render(self.message, True, self.border_color)
        message_rect = message_surface.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 50))
        self.screen.blit(message_surface, message_rect)

        option_y = message_rect.bottom + 30
        spacing = 120
        for idx, option in enumerate(self.options):
            is_selected = idx == self.selected_index
            color = self.border_color if is_selected else (200, 200, 200)
            option_surface = self.option_font.render(option.label, True, color)
            option_rect = option_surface.get_rect(center=(self.panel_rect.centerx + (idx - 0.5) * spacing, option_y))
            if is_selected:
                highlight_rect = option_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, color, highlight_rect, 2)
            self.screen.blit(option_surface, option_rect)


class SaveSlotMenu:
    """Menu for selecting a save/load slot."""

    def __init__(self, screen: pygame.Surface, slots: Sequence[str]) -> None:
        if not slots:
            raise ValueError("SaveSlotMenu requires at least one slot.")
        self.screen = screen
        self.slots = list(slots)
        self.visible = False
        self.mode = "save"
        self.selected_index = 0
        self.metadata: dict[str, dict[str, Any]] = {
            slot: {"status": "Empty", "player_name": None, "collection_owned": 0, "collection_total": 0}
            for slot in self.slots
        }
        self.overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.overlay_color = (0, 0, 0, 200)
        self.panel_rect = pygame.Rect(
            0, 0, int(self.screen.get_width() * 0.55), int(self.screen.get_height() * 0.65)
        )
        self.panel_rect.center = self.screen.get_rect().center
        self.title_font = pygame.font.Font(None, 50)
        self.slot_font = pygame.font.Font(None, 36)
        self.detail_font = pygame.font.Font(None, 24)
        self.active_color = (255, 255, 255)
        self.inactive_color = (170, 170, 190)

    def show(self, mode: str = "save") -> None:
        self.mode = mode
        self.selected_index = 0
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def set_metadata(self, metadata: dict[str, dict[str, Any]]) -> None:
        for slot in self.slots:
            if slot in metadata:
                self.metadata[slot] = metadata[slot]

    def move_selection(self, delta: int) -> None:
        self.selected_index = (self.selected_index + delta) % len(self.slots)

    def handle_key(self, key: int) -> tuple[str | None, str | None]:
        if key in (pygame.K_UP, pygame.K_w):
            self.move_selection(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.move_selection(1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE):
            return "confirm", self.slots[self.selected_index]
        elif key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self.hide()
            return "cancel", None
        return None, None

    def get_display_name(self, slot_name: str) -> str:
        slot = slot_name.lower()
        if slot.startswith("slot"):
            suffix = slot[4:]
            suffix = suffix.strip() or slot_name
            return f"Slot {suffix}".strip()
        return slot_name.title()

    def draw(self) -> None:
        if not self.visible:
            return
        self.overlay.fill(self.overlay_color)
        self.screen.blit(self.overlay, (0, 0))

        panel_surface = pygame.Surface(self.panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill((20, 20, 35, 240))
        pygame.draw.rect(panel_surface, self.active_color, panel_surface.get_rect(), 2)
        self.screen.blit(panel_surface, self.panel_rect.topleft)

        title_text = f"Select a slot to {self.mode.title()}"
        title_surface = self.title_font.render(title_text, True, self.active_color)
        title_rect = title_surface.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 50))
        self.screen.blit(title_surface, title_rect)

        slot_start_y = title_rect.bottom + 30
        row_height = 70
        for idx, slot in enumerate(self.slots):
            is_selected = idx == self.selected_index
            color = self.active_color if is_selected else self.inactive_color
            display_name = self.get_display_name(slot)
            meta = self.metadata.get(slot, {"status": "Empty"})

            label_surface = self.slot_font.render(display_name, True, color)
            label_rect = label_surface.get_rect()
            label_rect.centerx = self.panel_rect.centerx
            label_rect.y = slot_start_y + idx * row_height

            lines: list[str] = []
            if isinstance(meta, dict):
                status = meta.get("status", "")
                if status:
                    lines.append(status)
                player_name = meta.get("player_name")
                if player_name:
                    lines.append(f"Player: {player_name}")
                owned = meta.get("collection_owned")
                total = meta.get("collection_total")
                if owned is not None and total is not None and total > 0:
                    lines.append(f"Collection: {owned} / {total}")
            else:
                lines.append(str(meta))

            detail_bounds = None
            for line_idx, line in enumerate(lines):
                detail_surface = self.detail_font.render(line, True, color)
                detail_rect = detail_surface.get_rect()
                detail_rect.centerx = self.panel_rect.centerx
                detail_rect.y = label_rect.bottom + 5 + line_idx * (self.detail_font.get_height() + 2)
                self.screen.blit(detail_surface, detail_rect)
                if detail_bounds is None:
                    detail_bounds = detail_rect
                else:
                    detail_bounds = detail_bounds.union(detail_rect)

            if is_selected:
                highlight_target = label_rect if detail_bounds is None else label_rect.union(detail_bounds)
                highlight_rect = highlight_target.inflate(40, 20)
                pygame.draw.rect(self.screen, color, highlight_rect, 2)

            self.screen.blit(label_surface, label_rect)


class NotificationBanner:
    """Transient banner for save/load notifications."""

    def __init__(self, screen: pygame.Surface, default_duration: float = 2.5) -> None:
        self.screen = screen
        self.default_duration = default_duration
        self.remaining = 0.0
        self.message = ""
        self.font = pygame.font.Font(None, 32)
        self.background = pygame.Surface((self.screen.get_width(), 50), pygame.SRCALPHA)
        self.background_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)

    def show(self, message: str, duration: float | None = None) -> None:
        self.message = message
        self.remaining = duration if duration is not None else self.default_duration

    def update(self, dt: float) -> None:
        if self.remaining > 0:
            self.remaining -= dt
            if self.remaining <= 0:
                self.message = ""

    def draw(self) -> None:
        if self.remaining <= 0 or not self.message:
            return
        self.background.fill(self.background_color)
        text_surface = self.font.render(self.message, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.background.get_height() // 2))
        self.background.blit(text_surface, text_rect)
        self.screen.blit(self.background, (0, 10))
