from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict

try:
    from blake3 import blake3
except ImportError:  # pragma: no cover - fallback if blake3 is missing
    import hashlib

    def blake3(data: bytes):  # type: ignore
        class _Wrapper:
            def __init__(self, data: bytes):
                self._h = hashlib.sha256(data)

            def hexdigest(self) -> str:
                return self._h.hexdigest()

        return _Wrapper(data)


@dataclass(frozen=True)
class CardIdentity:
    """
    Canonical, namespaced card identity.

    - namespace: e.g. "PTCG", "FANMOD", "DEBUG"
    - definition_id: stable card definition identifier within that namespace
    - canonical_id: synthesized deterministic ID: "<ns>::<def_id>::<hash>"
    """

    namespace: str
    definition_id: str
    canonical_id: str


@dataclass(frozen=True)
class CardRevision:
    """Tracks a deterministic hash of persistent metadata for this instance."""

    hash: str


def _blake3_hex(data: bytes) -> str:
    return blake3(data).hexdigest()


def make_canonical_id(namespace: str, definition_id: str, hash_len: int = 8) -> CardIdentity:
    """
    Build a deterministic ID for a card definition, stable across runs.

    The hash is derived ONLY from (namespace, definition_id), not from
    player-specific metadata, so the identity does not change when the card
    levels up or gains XP.
    """
    base = f"{namespace}::{definition_id}".encode("utf-8")
    digest = _blake3_hex(base)[:hash_len]
    canonical_id = f"{namespace}::{definition_id}::{digest}"
    return CardIdentity(namespace=namespace, definition_id=definition_id, canonical_id=canonical_id)


def compute_revision(meta: Dict[str, Any] | None, hash_len: int = 10) -> CardRevision:
    """
    Compute a deterministic revision hash from persistent metadata.

    - Ignores key ordering via canonical JSON (sort_keys=True).
    - Intended for XP, level, unlock flags, cosmetics, etc.
    """
    meta = meta or {}
    payload = json.dumps(meta, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = _blake3_hex(payload)[:hash_len]
    return CardRevision(hash=digest)
