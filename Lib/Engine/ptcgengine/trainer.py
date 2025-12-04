from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .serialization import dump_canonical


@dataclass(frozen=True)
class Trainer:
    """
    Persistent trainer profile.

    Holds:
    - profile metadata (name, progression, cosmetics, etc.)
    - references to owned deck paths
    - active deck path
    """

    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    deck_paths: List[str] = field(default_factory=list)
    active_deck: str | None = None

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": dict(self.metadata),
            "deck_paths": list(self.deck_paths),
            "active_deck": self.active_deck,
        }

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "Trainer":
        return Trainer(
            name=data["name"],
            metadata=data.get("metadata", {}),
            deck_paths=list(data.get("deck_paths", [])),
            active_deck=data.get("active_deck"),
        )
