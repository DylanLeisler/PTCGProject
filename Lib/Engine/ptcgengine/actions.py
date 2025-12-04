"""
Defines the legal action structure used by the step() API.
All actions are plain dicts for easy serialization.
"""

# Action type identifiers
ATTACK = "attack"
PASS = "pass"
RETREAT = "retreat"
PLAY_CARD = "play_card"      # (stub for future)
USE_ABILITY = "use_ability"  # (stub)
ATTACH_ENERGY = "attach_energy"

def make_attack_action(attack_name: str):
    return {
        "type": ATTACK,
        "attack_name": attack_name,
    }

def make_pass_action():
    return {"type": PASS}

def make_retreat_action():
    return {"type": RETREAT}

def make_attach_energy_action(card_id: str, target: str = "self_active"):
    """
    card_id: ID of the energy card in hand to attach.
    target: string selector for now ("self_active" only in this MVP).
    """
    return {
        "type": ATTACH_ENERGY,
        "card_id": card_id,
        "target": target,
    }

# Stub for future expansion:
def make_play_card_action(card_id: str):
    return {
        "type": PLAY_CARD,
        "card_id": card_id,
    }
