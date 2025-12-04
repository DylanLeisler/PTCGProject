"""
Turn and phase management for the TCG engine.
"""

from .utils import trace

# Phases (simple for now)
PHASE_START = "start"
PHASE_MAIN = "main"
PHASE_ATTACK = "attack"
PHASE_END = "end"

def init_turn_flags(state):
    """Reset per-turn flags."""
    state.turn_flags = {
        "retreat_used": False,
        "attack_used": False,
        "energy_attached": False,
    }

def start_of_turn(state):
    """Handles draw step + resets flags."""
    player = state.players[state.active_player]
    if player.deck:
        player.hand.append(player.deck.pop())

    init_turn_flags(state)

    state.phase = PHASE_MAIN
    trace(f"Start of turn {state.turn}, player {state.active_player}")

def end_turn(state):
    """Switch active player and increment turn counter."""
    trace(f"Ending turn for player {state.active_player}")
    state.active_player = 1 - state.active_player
    state.turn += 1
    state.phase = PHASE_START

def apply_phase_transitions(state):
    """
    Ensures the correct phase logic is applied.
    Can be safely called multiple times; start_of_turn only fires once.
    """
    if state.phase == PHASE_START:
        start_of_turn(state)
