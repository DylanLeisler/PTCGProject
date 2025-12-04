from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .cards import BaseCard


@dataclass(frozen=True)
class CardDefinition:
    id: str
    name: str
    supertype: str
    hp: int
    image: Optional[str] = None


@dataclass
class EngineCardState:
    definition: CardDefinition | None
    current_hp: int
    status: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    hidden: bool = False

    _mutable_fields = {"definition", "current_hp", "status", "meta", "hidden", "_mutable_fields"}

    def __setattr__(self, name, value):
        # Allow normal initialization for known fields only
        if name in self._mutable_fields or name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        raise AttributeError(f"EngineCardState attribute '{name}' is immutable")

    def __post_init__(self):
        """
        Enforce model consistency:
        - Hidden cards may legally lack a definition (information masking).
        - Revealed/active cards MUST have a CardDefinition or this signals an engine bug.
        """
        if not self.hidden and self.definition is None:
            raise ValueError("EngineCardState requires a CardDefinition unless hidden=True.")


def _definition_from_engine(card: BaseCard) -> CardDefinition:
    image = None
    meta = getattr(card, "metadata", {}) or {}
    if isinstance(meta, dict):
        image = meta.get("image")
    return CardDefinition(
        id=getattr(card, "card_id", getattr(card, "id", "unknown")),
        name=getattr(card, "name", "Unknown"),
        supertype=getattr(card, "supertype", "unknown"),
        hp=getattr(card, "hp", getattr(card, "max_hp", 0)),
        image=image,
    )


def card_instance_from_engine(card: BaseCard | None) -> EngineCardState | None:
    if card is None:
        return None
    definition = _definition_from_engine(card)
    current_hp = getattr(card, "current_hp", getattr(card, "hp", 0))
    status = list(getattr(card, "status", []))
    meta = getattr(card, "metadata", {}) or {}
    return EngineCardState(definition=definition, current_hp=current_hp, status=status, meta=dict(meta))
