from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class GameEvent:
    """Immutable base event type."""

    type: str
    payload: Dict[str, Any]


def attack_event(source: str, target: str, damage: int) -> GameEvent:
    return GameEvent(
        type="attack",
        payload={"source": source, "target": target, "damage": damage},
    )


def status_event(effect: str, target: str) -> GameEvent:
    return GameEvent(
        type="status_effect",
        payload={"effect": effect, "target": target},
    )
