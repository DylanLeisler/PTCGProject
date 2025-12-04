"""
Renderer-friendly view of the engine state.
Uses card.snapshot() on each card instance.
"""

def render_state(state):
    return {
        "turn": state.turn,
        "active_player": state.active_player,
        "phase": state.phase,
        "players": [
            _view_player(state.players[0]),
            _view_player(state.players[1]),
        ],
    }

def _view_player(p):
    return {
        "active": p.active.snapshot() if p.active else None,
        "bench": [mon.snapshot() for mon in p.bench],
        "hand_count": len(p.hand),
        "deck_count": len(p.deck),
        "discard": [c.snapshot() for c in p.discard],
    }
