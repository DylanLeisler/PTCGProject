from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

from .card_identity import CardIdentity, CardRevision, compute_revision, make_canonical_id

DEFAULT_NAMESPACE = "PTCG"


@dataclass(frozen=True)
class CardInstance:
    """
    Persistent card instance owned by a player.

    - identity.canonical_id never changes (unless migrated explicitly).
    - revision.hash changes whenever persistent metadata changes.
    - meta contains persistent, non-battle attributes (xp, level, cosmetics, etc).
    """

    identity: CardIdentity
    revision: CardRevision
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def canonical_id(self) -> str:
        return self.identity.canonical_id

    @property
    def revision_hash(self) -> str:
        return self.revision.hash

    def with_updated_meta(self, meta: Dict[str, Any]) -> "CardInstance":
        """
        Return a new CardInstance with updated metadata and recomputed revision hash.

        identity (canonical_id) remains the same; only revision changes.
        """
        new_meta = dict(meta)
        new_rev = compute_revision(new_meta)
        return replace(self, meta=new_meta, revision=new_rev)


def create_instance(
    definition_id: str,
    meta: Optional[Dict[str, Any]] = None,
    namespace: str = DEFAULT_NAMESPACE,
) -> CardInstance:
    """
    Create a new CardInstance for a given card definition and namespace.

    - definition_id: logical ID in the card database (e.g. "PIKACHU-BASE")
    - namespace: "PTCG", "FANMOD", "DEBUG", etc.
    - meta: persistent, player-specific data (xp, level, unlock flags, etc.)
    """
    base_meta = dict(meta) if meta is not None else {}
    identity = make_canonical_id(namespace, definition_id)
    revision = compute_revision(base_meta)
    return CardInstance(identity=identity, revision=revision, meta=base_meta)
