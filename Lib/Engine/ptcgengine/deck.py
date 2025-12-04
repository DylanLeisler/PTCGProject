from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .card_instance import CardInstance, create_instance
from .serialization import dump_canonical


@dataclass(frozen=True)
class Deck:
    """An ordered, persistent deck of CardInstances."""

    name: str
    cards: List[CardInstance] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def shuffled(self, seed: int | None = None) -> "Deck":
        cards_copy = list(self.cards)
        rng = random.Random(seed)
        rng.shuffle(cards_copy)
        return Deck(name=self.name, cards=cards_copy, metadata=self.metadata)

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "cards": [
                {
                    "identity": c.identity.canonical_id,
                    "revision": c.revision.hash,
                    "meta": dict(c.meta),
                }
                for c in self.cards
            ],
            "metadata": dict(self.metadata),
        }

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "Deck":
        name = data["name"]
        meta = data.get("metadata", {})
        cards = [
            create_instance(
                definition_id=_extract_def_id(c["identity"]),
                meta=c.get("meta"),
                namespace=_extract_namespace(c["identity"]),
            )
            for c in data["cards"]
        ]
        return Deck(name=name, cards=cards, metadata=meta)


def _extract_namespace(canonical: str) -> str:
    return canonical.split("::")[0]


def _extract_def_id(canonical: str) -> str:
    return canonical.split("::")[1]
