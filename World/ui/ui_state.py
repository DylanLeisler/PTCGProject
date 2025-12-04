from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

try:
    from ptcgengine import api as engine_api
except Exception:  # pragma: no cover
    engine_api = None

ASSET_ROOT = Path(__file__).parent.parent / "assets"


def resolve_asset_path(rel: str | None) -> Optional[str]:
    if rel is None:
        return None
    p = Path(rel)
    if p.is_absolute():
        return str(p) if p.exists() else None
    candidate = ASSET_ROOT / p
    return str(candidate) if candidate.exists() else None


@dataclass(frozen=True)
class CardUIModel:
    name: str
    sprite_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    is_hidden: bool = False


@dataclass(frozen=True)
class OpponentHandUIModel:
    count: int = 0


@dataclass(frozen=True)
class PokemonView:
    name: str
    current_hp: Optional[int] = None
    max_hp: Optional[int] = None


@dataclass(frozen=True)
class BattleUIState:
    active_pokemon: Optional[PokemonView] = None
    opponent_pokemon: Optional[PokemonView] = None
    hand_size: int = 0
    hand_cards: List[CardUIModel] = field(default_factory=list)
    opponent_hand: OpponentHandUIModel | None = None
    actions: List[str] = field(default_factory=list)
    selected_action_index: int = 0
    log_lines: List[str] = field(default_factory=list)

    @staticmethod
    def from_engine_state(
        state: Any,
        actions: List[dict] | None,
        selected_action_index: int,
        log_lines: List[str],
    ) -> "BattleUIState":
        active_view = _extract_active_pokemon(state)
        opponent_view = _extract_opponent_pokemon(state)
        hand_cards = _extract_hand_cards(state)
        opp_hand = _extract_opponent_hand(state)

        action_labels: List[str] = []
        if actions:
            for a in actions:
                label = a.get("label") or a.get("type", "<?>")
                action_labels.append(str(label))

        log_strs = [str(line) for line in log_lines]

        return BattleUIState(
            active_pokemon=active_view,
            opponent_pokemon=opponent_view,
            hand_size=len(hand_cards) if hand_cards else _extract_hand_size(state),
            hand_cards=hand_cards,
            actions=action_labels,
            selected_action_index=max(0, min(selected_action_index, max(len(action_labels) - 1, 0))),
            log_lines=list(reversed(log_strs[-200:])),
            opponent_hand=opp_hand,
        )


def _extract_active_pokemon(state: Any) -> Optional[PokemonView]:
    if state is None:
        return None
    try:
        if engine_api is not None:
            active = engine_api.get_active(state)
            if active is not None:
                return PokemonView(
                    name=str(active.definition.name),
                    current_hp=getattr(active, "current_hp", None),
                    max_hp=getattr(active.definition, "hp", None),
                )
    except Exception:
        return None

    # Fallback: permissive getattr for dummy states
    try:
        player = getattr(state, "players", [None])[getattr(state, "active_player", 0)]
        active_slot = getattr(player, "active", None)
        if active_slot is None:
            return None
        name = getattr(active_slot, "name", None) or getattr(active_slot, "card_id", "Unknown")
        cur_hp = getattr(active_slot, "hp", None)
        max_hp = getattr(active_slot, "max_hp", None)
        return PokemonView(name=str(name), current_hp=cur_hp, max_hp=max_hp)
    except Exception:
        return None


def _extract_opponent_pokemon(state: Any) -> Optional[PokemonView]:
    if state is None:
        return None
    try:
        if engine_api is not None:
            active = engine_api.get_opponent_active(state)
            if active is not None:
                return PokemonView(
                    name=str(active.definition.name),
                    current_hp=getattr(active, "current_hp", None),
                    max_hp=getattr(active.definition, "hp", None),
                )
    except Exception:
        return None

    try:
        players = getattr(state, "players", None)
        idx = getattr(state, "active_player", 0)
        if not players or len(players) < 2:
            return None
        opp_idx = 1 - idx
        active_slot = getattr(players[opp_idx], "active", None)
        if active_slot is None:
            return None
        name = getattr(active_slot, "name", None) or getattr(active_slot, "card_id", "Unknown")
        cur_hp = getattr(active_slot, "hp", None)
        max_hp = getattr(active_slot, "max_hp", None)
        return PokemonView(name=str(name), current_hp=cur_hp, max_hp=max_hp)
    except Exception:
        return None


def _extract_hand_size(state: Any) -> int:
    if state is None:
        return 0
    try:
        if engine_api is not None:
            hand = engine_api.get_hand(state)
            return len(hand)
    except Exception:
        pass
    try:
        players = getattr(state, "players", None)
        idx = getattr(state, "active_player", 0)
        if players is None or not (0 <= idx < len(players)):
            return 0
        hand = getattr(players[idx], "hand", None)
        return len(hand) if hand is not None else 0
    except Exception:
        return 0


def _extract_opponent_hand(state: Any) -> OpponentHandUIModel | None:
    if state is None:
        return None
    try:
        if engine_api is not None:
            getter = getattr(engine_api, "get_opponent_hand", None)
            hand = getter(state) if getter else []
            hand = hand or []
            return OpponentHandUIModel(count=len(hand))
    except Exception:
        return None
    return None


def _extract_hand_cards(state: Any) -> List[CardUIModel]:
    models: List[CardUIModel] = []
    if state is None:
        return models
    try:
        if engine_api is not None:
            getter = getattr(engine_api, "get_human_hand", None) or getattr(engine_api, "get_hand", None)
            hand = getter(state) if getter else []
            hand = hand or []
            for c in hand:
                definition = getattr(c, "definition", None)
                name = getattr(definition, "name", None) or "Card"
                sprite_rel = getattr(definition, "image", None)
                sprite_path = resolve_asset_path(sprite_rel) if sprite_rel else None
                models.append(CardUIModel(name=str(name), sprite_path=sprite_path, is_hidden=getattr(c, "hidden", False)))
            return models
    except Exception:
        pass

    try:
        players = getattr(state, "players", None)
        idx = getattr(state, "active_player", 0)
        if players is None or not (0 <= idx < len(players)):
            return models
        hand = getattr(players[idx], "hand", None) or []
        for c in hand:
            name = getattr(c, "name", None) or getattr(c, "card_id", "Card")
            meta = getattr(c, "metadata", {}) or {}
            sprite_rel = getattr(c, "image", None) or meta.get("image")
            sprite_path = resolve_asset_path(sprite_rel) if sprite_rel else None
            models.append(CardUIModel(name=str(name), sprite_path=sprite_path))
        return models
    except Exception:
        return models
