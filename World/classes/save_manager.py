from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Sequence


@dataclass
class SaveState:
    area: str
    player: Dict[str, Any]
    timestamp: str
    collection: Dict[str, Any] | None = None


@dataclass
class GameState:
    area: str
    player_position: tuple[int, int]
    player_direction: str
    player_name: str
    collection_owned: int
    collection_total: int

    @classmethod
    def from_save_state(cls, state: SaveState) -> "GameState":
        player = state.player
        position = tuple(player.get("position", (0, 0)))
        direction = player.get("direction", "forward")
        name = player.get("name", "Player")
        collection = state.collection or {}
        owned = int(collection.get("owned", 0))
        total = int(collection.get("total", 0))
        return cls(
            area=state.area,
            player_position=position,
            player_direction=direction,
            player_name=name,
            collection_owned=owned,
            collection_total=total,
        )


class SaveManager:
    """Handles serialization of lightweight game state to JSON files."""

    DEFAULT_SAVE_DIR = Path(__file__).resolve().parents[2] / "data" / "saves"

    def __init__(self, save_dir: str | Path | None = None) -> None:
        self.save_dir = Path(save_dir) if save_dir is not None else self.DEFAULT_SAVE_DIR

    def build_state(self, *, area_name: str, player) -> SaveState:
        """Collect the minimal data we currently need to resume play."""
        player_state = {
            "name": getattr(player, "name", "Player"),
            "position": list(getattr(player, "position", (0, 0))),
            "direction": getattr(player, "direction", "forward"),
        }
        collection_state = {
            "owned": int(getattr(player, "collection_owned", 0)),
            "total": int(getattr(player, "collection_total", 0)),
        }
        return SaveState(
            area=area_name,
            player=player_state,
            timestamp=datetime.now(timezone.utc).isoformat(),
            collection=collection_state,
        )

    def _normalize_slot(self, slot_name: str) -> str:
        slot = slot_name.lower()
        return slot if slot.endswith(".json") else f"{slot}.json"

    def _slot_path(self, slot_name: str) -> Path:
        return self.save_dir / self._normalize_slot(slot_name)

    def save(self, state: SaveState, slot_name: str = "slot1") -> Path:
        """Write a SaveState to disk as JSON."""
        self.save_dir.mkdir(parents=True, exist_ok=True)
        path = self._slot_path(slot_name)
        with path.open("w", encoding="utf-8") as fp:
            json.dump(asdict(state), fp, indent=2)
        return path

    def load(self, slot_name: str = "slot1") -> GameState | None:
        """Return the saved state for the given slot, if it exists."""
        path = self._slot_path(slot_name)
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, json.JSONDecodeError):
            return None
        state = SaveState(**data)
        return GameState.from_save_state(state)

    def get_slot_metadata(self, slots: Sequence[str]) -> dict[str, Dict[str, Any]]:
        """Return friendly metadata for each requested slot."""
        metadata: dict[str, Dict[str, Any]] = {}
        for slot in slots:
            path = self._slot_path(slot)
            if not path.exists():
                metadata[slot] = {
                    "status": "Empty",
                    "player_name": None,
                    "collection_owned": 0,
                    "collection_total": 0,
                }
                continue
            try:
                with path.open("r", encoding="utf-8") as fp:
                    data = json.load(fp)
                timestamp = data.get("timestamp")
                player_name = data.get("player", {}).get("name")
                collection = data.get("collection", {}) or {}
            except (OSError, json.JSONDecodeError):
                metadata[slot] = {
                    "status": "Unreadable save",
                    "player_name": None,
                    "collection_owned": 0,
                    "collection_total": 0,
                }
                continue

            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    display = dt.astimezone().strftime("Saved %Y-%m-%d %H:%M")
                except ValueError:
                    display = f"Saved {timestamp}"
            else:
                display = "Occupied"
            metadata[slot] = {
                "status": display,
                "player_name": player_name,
                "collection_owned": int(collection.get("owned", 0)),
                "collection_total": int(collection.get("total", 0)),
            }
        return metadata
