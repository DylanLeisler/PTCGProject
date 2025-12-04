from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import pygame

from classes.card_manager import CardManager
from classes.characters.player import Player
from classes.graphics.camera import Camera
from classes.graphics.menu import (
    ConfirmDialog,
    DeckMenu,
    NotificationBanner,
    PauseMenu,
    SaveSlotMenu,
)
from classes.graphics.overworld.area import Area
from classes.graphics.overworld.inanimate import Inanimate
from classes.graphics.overworld.sprite_map import SpriteMap
from classes.graphics.sprite import AnimatedSprite
from classes.graphics.tile_ingester import Tile_Ingester
from classes.save_manager import GameState, SaveManager
from game_config import GameConfig as GC
from scenes.base_scene import BaseScene

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CARD_PATH = DATA_DIR / "cards" / "pokemon" / "sm10.json"
BASE_SET = DATA_DIR / "cards" / "sets" / "base1.json"
PLAYER_COLLECTION_PATH = DATA_DIR / "player_collection.json"
START_KEY = pygame.K_RETURN
AREA_SWITCH_KEY = pygame.K_TAB
COLLECTION_GAIN_KEY = pygame.K_c
SAVE_SLOTS = ("slot1", "slot2", "slot3")
DEFAULT_SLOT = SAVE_SLOTS[0]
NPC_GROUP_NAME = "npc"
INANIMATE_TYPES = ["wall", "object", "floor"]


def build_basic_area_specs(width: int, interior_rows: int) -> list[list[str]]:
    if width < 2:
        raise ValueError("width must be at least 2")
    specs: list[list[str]] = []
    top_row = ["top_left"] + ["top_center"] * (width - 2) + ["top_right"]
    specs.append(top_row)
    for _ in range(max(1, interior_rows)):
        specs.append(["side_center"] + ["floor"] * (width - 2) + ["side_center"])
    bottom_row = ["bottom_left"] + ["bottom_floor"] * (width - 2) + ["bottom_right"]
    specs.append(bottom_row)
    specs.append(["bottom_center"] * width)
    specs.append(["bottom_shadow"] * width)
    return specs


def load_player_collection(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
        cards = data.get("owned_cards", [])
        filtered = [card_id for card_id in cards if isinstance(card_id, str)]
        return list(dict.fromkeys(filtered))
    except (OSError, json.JSONDecodeError):
        return []


def write_player_collection(path: Path, card_ids: list[str]) -> None:
    payload = {"owned_cards": card_ids}
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)


def build_card_library(paths: tuple[str | Path, ...]) -> CardManager:
    if not paths:
        raise ValueError("At least one card file path is required.")
    normalized_paths = tuple(Path(p) for p in paths)
    iterator = iter(normalized_paths)
    master = CardManager(next(iterator))
    for path in iterator:
        master = master + CardManager(path)
    return master


def build_collection_entries(card_ids: list[str], library: CardManager) -> tuple[list[dict[str, Any]], dict[str, int]]:
    entries: list[dict[str, Any]] = []
    summary: dict[str, int] = {"Pokemon": 0, "Trainer": 0, "Energy": 0, "Unknown": 0}
    supertype_priority = {"Pokemon": 0, "Trainer": 1, "Energy": 2}

    for card_id in card_ids:
        card = library.get_card_by_id(card_id) if library else None
        name = getattr(card, "name", "Unknown Card")
        supertype = getattr(card, "supertype", None) or card.__class__.__name__ if card else "Unknown"
        supertype = supertype or "Unknown"
        summary.setdefault(supertype, 0)
        summary[supertype] += 1
        entries.append(
            {
                "id": card_id,
                "name": name,
                "supertype": supertype,
                "card": card,
                "description": getattr(card, "description", ""),
            }
        )

    entries.sort(key=lambda entry: (supertype_priority.get(entry["supertype"], 3), entry["name"], entry["id"]))
    summary["Total"] = len(entries)
    summary["Available"] = library.total_unique_cards() if library else len(entries)
    return entries, summary


class OverworldScene(BaseScene):
    def __init__(self, screen: pygame.Surface, scene_manager) -> None:
        self.screen = screen
        self.scene_manager = scene_manager
        self.pending_confirmation: dict | None = None

        self.card_library = build_card_library((CARD_PATH, BASE_SET))
        self.total_collection_cards = self.card_library.total_unique_cards()
        self.owned_card_ids = load_player_collection(PLAYER_COLLECTION_PATH)
        self.collection_entries, self.collection_summary = build_collection_entries(
            self.owned_card_ids, self.card_library
        )

        self.lab_tiles = Tile_Ingester().build_index().get_index()
        self.overworld_sprites = self._load_overworld_sprite_assets()
        self.area_definitions = self._build_area_definitions()
        self.area_spawns = {
            "LAB": GC.PLAYER_STARTING_POSITION,
            "COURTYARD": (GC.TILE_SIZE * 2, GC.TILE_SIZE * 2),
        }
        self.area_sequence = list(self.area_definitions.keys())

        self.groups = {name: pygame.sprite.Group() for name in ["player", NPC_GROUP_NAME, *INANIMATE_TYPES]}
        self.current_area_name = "LAB"
        self.current_area = self._create_area(self.current_area_name)
        self.player = self._make_player().add_to_group(self.groups)
        self._sync_player_collection()

        self.pause_menu = PauseMenu(screen)
        self.deck_menu = DeckMenu(screen)
        self.confirm_dialog = ConfirmDialog(screen)
        self.slot_menu = SaveSlotMenu(screen, SAVE_SLOTS)
        self.notification = NotificationBanner(screen)
        self.save_manager = SaveManager()

        self.last_movement_key: int | None = None
        self.movement_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]
        self.deck_menu.set_deck_data(self.collection_entries, self.collection_summary)
        base_view_size = self.current_area.get_world_size()
        self.camera = Camera(
            (GC.SCREEN_WIDTH, GC.SCREEN_HEIGHT),
            self.current_area.get_world_size(),
            base_view_size,
            GC.MAX_CAMERA_ZOOM,
            constrain_to_world=False,
        )
        self.camera.update(self.player.rect)

        self._restore_initial_state()

    def update(self, dt: float) -> None:
        overlays_blocking = (
            self.pause_menu.visible or self.deck_menu.visible or self.confirm_dialog.visible or self.slot_menu.visible
        )
        if overlays_blocking:
            self.player.update(dt, reset_frame=True)
        else:
            key = pygame.key.get_pressed()
            movement_keys_pressed = [k for k in self.movement_keys if key[k]]
            num_movement_keys_pressed = len(movement_keys_pressed)
            moved_this_frame = False

            if num_movement_keys_pressed > 0:
                if num_movement_keys_pressed > 1:
                    for pressed in movement_keys_pressed:
                        if pressed == self.last_movement_key:
                            continue
                        moved_this_frame = True
                        self.player.move(pressed, dt, self.groups)
                        break
                else:
                    self.last_movement_key = movement_keys_pressed[0]
                    moved_this_frame = True
                    self.player.move(movement_keys_pressed[0], dt, self.groups)

            if not moved_this_frame:
                self.player.update(dt, reset_frame=True)

        self.camera.update(self.player.rect)
        self.notification.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        if not self.current_area:
            return

        self.camera.begin_draw()
        self._render_map(self.current_area, self.camera)
        image = self.player.get_frame()
        self.camera.blit(image, self.player.visual_position)

        collision_layer = pygame.Surface((self.player.collision_rect.width, self.player.collision_rect.height), pygame.SRCALPHA)
        non_layer = pygame.Surface((self.player.rect.width, self.player.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(collision_layer, (255, 0, 0, 150), collision_layer.get_rect())
        pygame.draw.rect(non_layer, (0, 255, 0, 75), non_layer.get_rect())

        self.camera.blit(collision_layer, self.player.collision_rect.topleft)
        self.camera.blit(non_layer, self.player.rect.topleft)
        self.camera.present(screen)

        if self.pause_menu.visible:
            self.pause_menu.draw()
        if self.deck_menu.visible:
            self.deck_menu.draw()
        if self.slot_menu.visible:
            self.slot_menu.draw()
        if self.confirm_dialog.visible:
            self.confirm_dialog.draw()

        self.notification.draw()

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if self.confirm_dialog.visible:
                self._handle_confirmation_input(event.key)
                return

            if self.slot_menu.visible:
                action, selected_slot = self.slot_menu.handle_key(event.key)
                if action == "confirm" and selected_slot:
                    slot_label = self.slot_menu.get_display_name(selected_slot)
                    slot_meta = self.slot_menu.metadata.get(selected_slot, {})
                    status = slot_meta.get("status") if isinstance(slot_meta, dict) else str(slot_meta)
                    if self.slot_menu.mode == "save":
                        if status == "Unreadable save":
                            message = f"Overwrite corrupted data in {slot_label}?"
                        elif status == "Empty":
                            message = f"Save to {slot_label}?"
                        else:
                            message = f"Overwrite {slot_label}?"
                        self._show_confirmation("save", message, slot=selected_slot, label=slot_label)
                    else:
                        if status == "Unreadable save":
                            self.notification.show("Save data is corrupt")
                        elif status == "Empty":
                            self.notification.show("Slot is empty")
                        else:
                            message = f"Load {slot_label}? Unsaved progress will be lost."
                            self._show_confirmation("load", message, slot=selected_slot, label=slot_label)
                elif action == "cancel":
                    self.slot_menu.hide()
                    self.pause_menu.show()
                return

            if self.deck_menu.visible:
                deck_action = self.deck_menu.handle_key(event.key)
                if deck_action == "back":
                    self.deck_menu.hide()
                    self.pause_menu.show()
                return

            if event.key == START_KEY:
                if self.pause_menu.visible:
                    self.pause_menu.hide()
                else:
                    self.pause_menu.show()
                return

            if self.pause_menu.visible:
                action = self.pause_menu.handle_key(event.key)
                if action == "resume":
                    self.pause_menu.hide()
                elif action == "deck":
                    self.pause_menu.hide()
                    self.deck_menu.show()
                elif action == "save":
                    self.pause_menu.hide()
                    self._open_slot_menu("save")
                elif action == "load":
                    self.pause_menu.hide()
                    self._open_slot_menu("load")
                elif action == "quit":
                    self.pause_menu.hide()
                    self._show_confirmation("quit", "Exit the game?")
                return

            overlays_blocking = (
                self.pause_menu.visible
                or self.deck_menu.visible
                or self.slot_menu.visible
                or self.confirm_dialog.visible
            )
            if overlays_blocking:
                return

            # ---- Battle Trigger ----
            # Temporarily allow manual battle trigger via E or Enter.
            if event.key in (pygame.K_e, pygame.K_RETURN):
                if self._can_trigger_battle():
                    from scenes import battle_scene as bs

                    # Prefer the API already loaded in battle_scene (so tests can monkeypatch it).
                    engine_api = getattr(bs, "api", None)
                    if engine_api is None:
                        try:
                            from ptcgengine import api as engine_api  # type: ignore
                        except Exception:
                            engine_api = None

                    initial_state = None
                    if engine_api is not None:
                        try:
                            initial_state = engine_api.initial_state()
                        except Exception:
                            initial_state = None

                    battle = bs.BattleScene(self.screen, self.scene_manager, initial_state=initial_state)
                    self.scene_manager.push(battle)
                return

            if event.key == COLLECTION_GAIN_KEY:
                self._award_random_card()
                return
            if event.key == AREA_SWITCH_KEY:
                self._cycle_area(1)
                return

    def _load_overworld_sprite_assets(self) -> dict[str, pygame.Surface]:
        sprites: dict[str, pygame.Surface] = {}
        sprite_dir = DATA_DIR / "overworld_sprites"

        def apply_dark_transparency(surface: pygame.Surface, threshold: int = 16) -> pygame.Surface:
            width, height = surface.get_size()
            masked = pygame.Surface((width, height), pygame.SRCALPHA)
            src = surface.convert()
            for y in range(height):
                for x in range(width):
                    color = src.get_at((x, y))
                    if max(color.r, color.g, color.b) > threshold:
                        masked.set_at((x, y), color)
            return masked

        def extract_sprite(
            sheet: pygame.Surface,
            frame_size: tuple[int, int],
            coord: tuple[int, int],
            *,
            scale: tuple[int, int] | None = None,
            mask_dark: bool = False,
        ) -> pygame.Surface:
            frame_rect = pygame.Rect(coord[0] * frame_size[0], coord[1] * frame_size[1], *frame_size)
            fragment = pygame.Surface(frame_rect.size, pygame.SRCALPHA)
            fragment.blit(sheet, (0, 0), frame_rect)
            if mask_dark:
                fragment = apply_dark_transparency(fragment)
            if scale is not None and fragment.get_size() != scale:
                fragment = pygame.transform.smoothscale(fragment, scale)
            return fragment.convert_alpha()

        target_scale = (GC.TILE_SIZE, GC.TILE_SIZE)

        lillie_sheet = pygame.image.load(sprite_dir / "lillie.png").convert()
        lillie_frames = {
            "lillie_front": (4, 4),
            "lillie_side": (4, 3),
            "lillie_back": (4, 5),
        }
        for key, coord in lillie_frames.items():
            sprites[key] = extract_sprite(
                lillie_sheet,
                (64, 64),
                coord,
                scale=target_scale,
                mask_dark=True,
            )

        gbc_sheet = pygame.image.load(sprite_dir / "GBC_PTCG2_OVERWORLD_SPRITE_MAP.png").convert_alpha()
        gbc_frame_size = (16, 16)
        gbc_scale = (GC.SPRITE_LENGTH * 3, int(GC.SPRITE_LENGTH * 3))
        gbc_definitions = {
            "gbc_scientist": (0, 0),
            "gbc_cooltrainer": (4, 0),
            "gbc_fisher": (8, 0),
        }
        for name, coord in gbc_definitions.items():
            sprites[name] = extract_sprite(gbc_sheet, gbc_frame_size, coord, scale=gbc_scale)

        return sprites

    def _build_area_definitions(self) -> dict[str, dict[str, Any]]:
        map_data = {"area": "LAB", "specs": build_basic_area_specs(8, 4)}
        courtyard_specs = build_basic_area_specs(16, 10)
        for row_index in range(2, min(len(courtyard_specs) - 3, 6)):
            row = courtyard_specs[row_index]
            row[3:5] = ["bottom_floor", "bottom_floor"]
        courtyard_map = {"area": "LAB", "specs": courtyard_specs}
        return {
            "LAB": map_data,
            "COURTYARD": courtyard_map,
        }

    def _populate_area_static_sprites(self, area_name: str, area: Area) -> None:
        entries: dict[str, list[dict[str, object]]] = {
            "LAB": [
                {"sprite": "lillie_front", "tile": (4, 3), "group": NPC_GROUP_NAME},
            ],
            "COURTYARD": [
                {"sprite": "gbc_scientist", "tile": (6, 5), "group": NPC_GROUP_NAME},
                {"sprite": "gbc_cooltrainer", "tile": (10, 6), "group": NPC_GROUP_NAME},
                {"sprite": "gbc_fisher", "tile": (3, 8), "group": NPC_GROUP_NAME},
            ],
        }
        area_entries = entries.get(area_name.upper())
        if not area_entries:
            return
        for entry in area_entries:
            sprite_key = entry.get("sprite")
            if not isinstance(sprite_key, str):
                continue
            sprite_surface = self.overworld_sprites.get(sprite_key)
            if sprite_surface is None:
                continue
            offset_x, offset_y = entry.get("offset", (0, 0))
            tile = entry.get("tile")
            if tile is not None:
                tile_x, tile_y = tile
                base_x = tile_x * GC.TILE_SIZE
                base_y = tile_y * GC.TILE_SIZE
                width, height = sprite_surface.get_size()
                position = (
                    base_x + (GC.TILE_SIZE - width) // 2 + offset_x,
                    base_y + GC.TILE_SIZE - height + offset_y,
                )
            else:
                pos = entry.get("position", (0, 0))
                if isinstance(pos, (list, tuple)):
                    position = (pos[0] + offset_x, pos[1] + offset_y)
                else:
                    position = (offset_x, offset_y)
            npc = Inanimate(sprite_surface, [int(position[0]), int(position[1])])
            area.inanimates.append(npc)
            group_name = entry.get("group", NPC_GROUP_NAME)
            if not isinstance(group_name, str):
                group_name = NPC_GROUP_NAME
            self.groups.setdefault(group_name, pygame.sprite.Group()).add(npc)
            if entry.get("collision"):
                self.groups.setdefault("wall", pygame.sprite.Group()).add(npc)

    def _clear_inanimate_groups(self) -> None:
        for group_name in INANIMATE_TYPES:
            self.groups[group_name].empty()
        if NPC_GROUP_NAME in self.groups:
            self.groups[NPC_GROUP_NAME].empty()

    def _create_area(self, area_name: str) -> Area:
        Area.OFFSET = {"x": 0, "y": 0}
        self._clear_inanimate_groups()
        instructions = self.area_definitions.get(area_name.upper(), self.area_definitions[self.current_area_name])
        area = Area(self.screen, self.lab_tiles, instructions, (GC.SCREEN_WIDTH, GC.SCREEN_HEIGHT), self.groups)
        self._populate_area_static_sprites(area_name, area)
        return area

    @staticmethod
    def _get_basic_animated_sprite_coords(y, groupings=[3, 3, 2, 2]):
        index_pos = 0
        ll_coords = []
        for group in groupings:
            ll_coords.append([(x + index_pos, y) for x in range(group)])
            index_pos += group
        return ll_coords

    def _make_player(self, animated_sprite_coords=None) -> Player:
        sprite_handler = SpriteMap(
            GC.SPRITE_MAP_PATH,
            transparent_color=GC.ALPHA_COLOR_KEY,
            sprite_dimensions=(GC.SPRITE_LENGTH, GC.SPRITE_HEIGHT),
            left_border=GC.LEFT_BORDER,
            top_border=GC.TOP_BORDER,
            between_border=GC.BETWEEN_BORDER,
        )
        coords = animated_sprite_coords or self._get_basic_animated_sprite_coords(1)
        player_sprite = AnimatedSprite(sprite_handler.get_animated_sprite(*coords))
        return Player(player_sprite, "Player")

    def _render_map(self, area: Area, camera: Camera) -> None:
        view_rect = camera.get_view_rect()
        inanimates = area.get_inanimates()
        for inanimate in inanimates:
            if not view_rect.colliderect(inanimate.rect):
                continue
            camera.blit(inanimate.image, inanimate.visual_position)

    def _sync_player_collection(self) -> None:
        self.player.collection_owned = len(self.owned_card_ids)
        self.player.collection_total = self.total_collection_cards or self.player.collection_total

    def _refresh_collection_views(self) -> None:
        self.collection_entries, self.collection_summary = build_collection_entries(
            self.owned_card_ids, self.card_library
        )
        self.deck_menu.set_deck_data(self.collection_entries, self.collection_summary)
        self._sync_player_collection()

    def _persist_collection(self) -> None:
        write_player_collection(PLAYER_COLLECTION_PATH, self.owned_card_ids)

    def _award_random_card(self) -> None:
        available_ids = [cid for cid in self.card_library.card_index.keys() if cid not in self.owned_card_ids]
        if not available_ids:
            self.notification.show("Collection complete!")
            return
        new_card_id = random.choice(available_ids)
        self.owned_card_ids.append(new_card_id)
        self._persist_collection()
        self._refresh_collection_views()
        card = self.card_library.get_card_by_id(new_card_id)
        card_name = getattr(card, "name", new_card_id)
        self.notification.show(f"New card acquired: {card_name}")

    def _cycle_area(self, direction: int = 1) -> None:
        if not self.area_sequence:
            return
        idx = self.area_sequence.index(self.current_area_name)
        self.current_area_name = self.area_sequence[(idx + direction) % len(self.area_sequence)]
        self.current_area = self._create_area(self.current_area_name)
        spawn_point = self.area_spawns.get(self.current_area_name, GC.PLAYER_STARTING_POSITION)
        self._set_player_position(spawn_point)
        area_size = self.current_area.get_world_size()
        self.camera.set_world_size(area_size)
        self.camera.update(self.player.rect)
        self.notification.show(f"Entered {self.current_area_name.title()}")

    def _can_trigger_battle(self) -> bool:
        """
        Temporary placeholder used during early testing.
        Returns True so pressing E or Enter initiates a battle.

        Later, replace with collision-based NPC proximity or tile triggers.
        """
        return True

    def _open_slot_menu(self, mode: str) -> None:
        self.slot_menu.set_metadata(self.save_manager.get_slot_metadata(SAVE_SLOTS))
        self.slot_menu.show(mode)

    def _show_confirmation(self, kind: str, message: str, **payload) -> None:
        self.pending_confirmation = {"type": kind, **payload}
        self.confirm_dialog.show(message)

    def _handle_confirmation_input(self, key: int) -> None:
        decision = self.confirm_dialog.handle_key(key)
        if decision == "yes":
            if self.pending_confirmation:
                pending_type = self.pending_confirmation.get("type")
                if pending_type == "quit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                elif pending_type == "save":
                    slot_name = self.pending_confirmation.get("slot")
                    slot_label = self.pending_confirmation.get("label", slot_name)
                    try:
                        self._save_game(slot_name)
                        self.notification.show(f"Saved to {slot_label}")
                    except Exception as exc:  # pragma: no cover - UI display path
                        self.notification.show(f"Save failed: {exc}")
                        self.confirm_dialog.hide()
                        self.pending_confirmation = None
                        return
                    self.slot_menu.hide()
                    self.pause_menu.show()
                elif pending_type == "load":
                    slot_name = self.pending_confirmation.get("slot")
                    slot_label = self.pending_confirmation.get("label", slot_name)
                    loaded_state = self._load_game_from_slot(slot_name)
                    if loaded_state:
                        self.current_area_name = loaded_state.area.upper()
                        self.current_area = self._create_area(self.current_area_name)
                        area_size = self.current_area.get_world_size()
                        self.camera.set_world_size(area_size)
                        self.camera.update(self.player.rect)
                        self.notification.show(f"Loaded {slot_label}")
                        self.slot_menu.hide()
                        self.pause_menu.show()
                    else:
                        self.notification.show("Slot is empty")
                        self.confirm_dialog.hide()
                        self.pending_confirmation = None
                        return
            self.confirm_dialog.hide()
            self.pending_confirmation = None
        elif decision == "no":
            current_type = self.pending_confirmation.get("type") if self.pending_confirmation else None
            self.confirm_dialog.hide()
            if current_type == "quit":
                self.pause_menu.show()
            self.pending_confirmation = None

    def _save_game(self, slot_name: str) -> str:
        state = self.save_manager.build_state(area_name=self.current_area_name, player=self.player)
        save_path = self.save_manager.save(state, slot_name)
        return str(save_path)

    def _load_game_from_slot(self, slot_name: str) -> GameState | None:
        state = self.save_manager.load(slot_name)
        if state is None:
            return None
        self._apply_state_to_player(state)
        return state

    def _apply_state_to_player(self, state: GameState) -> None:
        self._set_player_position(state.player_position)
        self.player.direction = state.player_direction
        self.player.name = state.player_name
        self._sync_player_collection()

    def _set_player_position(self, target_pos: tuple[int, int]) -> None:
        current_x, current_y = self.player.rect.topleft
        dx = target_pos[0] - current_x
        dy = target_pos[1] - current_y
        self.player.position = (dx, dy)

    def _restore_initial_state(self) -> None:
        initial_state = self.save_manager.load(DEFAULT_SLOT)
        if initial_state:
            self._apply_state_to_player(initial_state)
            if initial_state.area.upper() != self.current_area_name:
                self.current_area_name = initial_state.area.upper()
                self.current_area = self._create_area(self.current_area_name)
                area_size = self.current_area.get_world_size()
                self.camera.set_world_size(area_size)
            self.camera.update(self.player.rect)
