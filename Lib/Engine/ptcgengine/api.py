from .action_generation import get_available_actions as _inner_actions
from .actions import ATTACH_ENERGY, ATTACK, PASS, RETREAT
from .context import EffectContext
from .interpreter import execute_effect
from .state import GameState
from .turn_manager import PHASE_MAIN, apply_phase_transitions, end_turn
from .view import render_state
from .card_models import card_instance_from_engine, EngineCardState


def initial_state(deck=None, trainer=None):
    """
    Create an initial GameState with optional deck and trainer metadata.

    Decks are shuffled copies to avoid mutation of the persistent definition.
    """
    state = GameState()

    if trainer:
        state.trainer = trainer

    if deck:
        state.deck = deck.shuffled()

    return state

def get_available_actions(state, card_db=None):
    return _inner_actions(state, card_db)

def step(state, action, card_db=None):
    """
    Applies the action and returns a tuple:
      (next_state, list_of_new_events)

    Next state contains the updated full event log.
    """
    state = state.clone()
    apply_phase_transitions(state)
    new_events = []

    if state.phase == PHASE_MAIN:
        new_events = _apply_main_phase_action(state, action, card_db)

    state.event_log = list(state.event_log) + new_events
    return state, new_events


# ---------------------------
# UI-facing accessors
# ---------------------------
def get_active(state) -> EngineCardState | None:
    try:
        ap = getattr(state, "active_player", 0)
        players = getattr(state, "players", [])
        if not players:
            return None
        return card_instance_from_engine(players[ap].active)
    except Exception:
        return None


def get_opponent_active(state) -> EngineCardState | None:
    try:
        ap = getattr(state, "active_player", 0)
        players = getattr(state, "players", [])
        if len(players) < 2:
            return None
        opp = 1 - ap
        return card_instance_from_engine(players[opp].active)
    except Exception:
        return None


def get_hand(state) -> list[EngineCardState]:
    try:
        ap = getattr(state, "active_player", 0)
        players = getattr(state, "players", [])
        if not players:
            return []
        hand = getattr(players[ap], "hand", []) or []
        return [ci for ci in (card_instance_from_engine(c) for c in hand) if ci is not None]
    except Exception:
        return []

# Perspective-aware accessors (human = player 0 for now)
def get_human_entity(state) -> EngineCardState | None:
    try:
        players = getattr(state, "players", [])
        if not players:
            return None
        return card_instance_from_engine(players[0].active)
    except Exception:
        return None


def get_opponent_entity(state) -> EngineCardState | None:
    try:
        players = getattr(state, "players", [])
        if len(players) < 2:
            return None
        return card_instance_from_engine(players[1].active)
    except Exception:
        return None


def get_active_entity(state) -> EngineCardState | None:
    return get_human_entity(state)


def get_human_hand(state) -> list[EngineCardState]:
    try:
        players = getattr(state, "players", [])
        if not players:
            return []
        hand = getattr(players[0], "hand", []) or []
        return [ci for ci in (card_instance_from_engine(c) for c in hand) if ci is not None]
    except Exception:
        return []


def get_opponent_hand(state) -> list[EngineCardState]:
    try:
        players = getattr(state, "players", [])
        if len(players) < 2:
            return []
        raw = getattr(players[1], "hand", []) or []
        # Only provide count/hidden markers; no definitions to avoid leaking info.
        return [EngineCardState(definition=None, current_hp=0, hidden=True) for _ in raw]
    except Exception:
        return []

def _apply_main_phase_action(state, action, card_db):
    t = action["type"]
    ap = state.active_player
    p = state.players[ap]

    if t == ATTACK:
        events = _apply_attack(state, action, card_db)
        state.turn_flags["attack_used"] = True
        end_turn(state)
        return events

    if t == ATTACH_ENERGY:
        _apply_attach_energy(state, action, card_db)
        state.turn_flags["energy_attached"] = True
        return []

    if t == RETREAT:
        state.turn_flags["retreat_used"] = True
        return []

    if t == PASS:
        end_turn(state)
        return []

    raise ValueError(f"Unknown action {t}")

def _apply_attack(state, action, card_db):
    ap = state.active_player
    mon = state.players[ap].active

    atk_name = action["attack_name"]
    try:
        atk = next(a for a in mon.attacks if a["name"] == atk_name)
    except StopIteration:
        raise ValueError(
            f"Attack {atk_name} not found on {mon.card_id}"
        ) from None

    effect = atk.get("effect")
    events = []
    if effect:
        ctx = EffectContext(controller=ap)
        state, events = execute_effect(effect, state, ctx)

    return events

def _apply_attach_energy(state, action, card_db):
    ap = state.active_player
    p = state.players[ap]
    cid = action["card_id"]

    # Find card instance
    for c in p.hand:
        if c.card_id == cid:
            card = c
            break
    else:
        raise ValueError(f"Energy card {cid} not in hand")

    target = p.active
    if not target:
        raise ValueError("No active Pokémon to attach to")

    # Move card
    p.hand.remove(card)
    target.attached_energies.append(card)
