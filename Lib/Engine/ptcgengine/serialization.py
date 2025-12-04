"""
Canonical JSON serialization utilities for Trainer and Deck.

Rules:
- Deterministic key ordering
- Canonical compact format (no whitespace padding)
- Friendly for Git diffs and content-addressable hashing later
"""

from __future__ import annotations
import json
from typing import Any


def dump_canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def save_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(dump_canonical(data))


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
