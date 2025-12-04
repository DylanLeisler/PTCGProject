"""
Card dataclasses + factory functions for instantiating gameplay cards.

These objects live ONLY inside the engine. The UI receives dict snapshots
through render_state() and never touches these dataclasses.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class BaseCard:
    card_id: str
    supertype: str
    name: str
    # Additional metadata (stage, set, etc.) stored for engine rules only
    metadata: Dict[str, Any] = field(default_factory=dict)

    def snapshot(self):
        """Public renderer-facing dict."""
        return {
            "card_id": self.card_id,
            "name": self.name,
            "supertype": self.supertype,
        }

@dataclass
class PokemonCard(BaseCard):
    hp: int = 0
    types: List[str] = field(default_factory=list)
    attacks: List[Dict[str, Any]] = field(default_factory=list)
    retreat_cost: List[str] = field(default_factory=list)

    # Runtime state (NOT in card_db; mutable during battle)
    current_hp: int = 0
    attached_energies: List["EnergyCard"] = field(default_factory=list)
    status: set = field(default_factory=set)

    def snapshot(self):
        return {
            "card_id": self.card_id,
            "name": self.name,
            "supertype": self.supertype,
            "hp": self.current_hp,
            "max_hp": self.hp,
            "types": list(self.types),
            "energies": [e.card_id for e in self.attached_energies],
            "status": list(self.status),
        }

@dataclass
class EnergyCard(BaseCard):
    energy_type: str = ""

    def snapshot(self):
        return {
            "card_id": self.card_id,
            "name": self.name,
            "supertype": self.supertype,
            "energy_type": self.energy_type,
        }

@dataclass
class TrainerCard(BaseCard):
    # Stub for future expansion
    effect: Dict[str, Any] = field(default_factory=dict)

    def snapshot(self):
        return {
            "card_id": self.card_id,
            "name": self.name,
            "supertype": self.supertype,
        }


###############################################################
# CARD FACTORY FUNCTIONS
###############################################################

def create_card_instance(card_id: str, card_db: Dict[str, Any]):
    entry = card_db.get(card_id)
    if entry is None:
        raise ValueError(f"card_id {card_id} not found in DB")

    supertype = entry.get("supertype")
    name = entry.get("name", card_id)

    if supertype == "pokemon":
        return PokemonCard(
            card_id=card_id,
            supertype="pokemon",
            name=name,
            hp=entry["hp"],
            current_hp=entry["hp"],
            types=entry.get("types", []),
            attacks=entry.get("attacks", []),
            retreat_cost=entry.get("retreat_cost", []),
            metadata={k: v for k, v in entry.items()
                      if k not in ("hp", "types", "attacks", "retreat_cost")}
        )

    if supertype == "energy":
        return EnergyCard(
            card_id=card_id,
            supertype="energy",
            name=name,
            energy_type=entry.get("energy_type", ""),
            metadata={k: v for k, v in entry.items()
                      if k not in ("energy_type",)}
        )

    if supertype == "trainer":
        return TrainerCard(
            card_id=card_id,
            supertype="trainer",
            name=name,
            effect=entry.get("effect", {}),
            metadata={k: v for k, v in entry.items()
                      if k != "effect"}
        )

    raise ValueError(f"Unsupported card supertype: {supertype}")
