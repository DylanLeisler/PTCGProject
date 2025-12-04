"""
Updated to handle card objects instead of raw IDs.
"""

from .actions import (
    make_attack_action, make_pass_action,
    make_retreat_action, make_attach_energy_action
)
from .turn_manager import PHASE_MAIN, apply_phase_transitions
from .energy import has_energy_for_cost

def get_available_actions(state, card_db=None):
    local = state.clone()
    apply_phase_transitions(local)

    p = local.players[local.active_player]
    actions = []

    if local.phase == PHASE_MAIN:
        # Attacks
        mon = p.active
        if mon and not local.turn_flags.get("attack_used", False):
            for atk in mon.attacks:
                if card_db is None or has_energy_for_cost(mon, atk["cost"], card_db):
                    actions.append(make_attack_action(atk["name"]))

        # Energy attachment
        if not local.turn_flags.get("energy_attached", False):
            for c in p.hand:
                if c.supertype == "energy":
                    actions.append(make_attach_energy_action(c.card_id, "self_active"))

        # Retreat (placeholder)
        if not local.turn_flags.get("retreat_used", False):
            actions.append(make_retreat_action())

        actions.append(make_pass_action())

    return actions
