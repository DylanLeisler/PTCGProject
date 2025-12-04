"""
Cost evaluation adapted for EnergyCard objects.
"""

from collections import Counter
from .cards import EnergyCard, PokemonCard

def get_pokemon_energy_pool(pokemon: PokemonCard):
    types = [e.energy_type for e in pokemon.attached_energies]
    return Counter(types)

def has_energy_for_cost(pokemon: PokemonCard, cost, card_db=None):
    if not cost:
        return True

    pool = get_pokemon_energy_pool(pokemon)
    typed_reqs = []
    colorless = 0

    for sym in cost:
        if sym == "C":
            colorless += 1
        else:
            typed_reqs.append(sym)

    pool = pool.copy()
    for t in typed_reqs:
        if pool[t] <= 0:
            return False
        pool[t] -= 1

    return sum(pool.values()) >= colorless
