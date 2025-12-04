from ptcgengine.state import GameState
from ptcgengine.cards import PokemonCard, BaseCard
from ptcgengine.context import EffectContext
from ptcgengine.interpreter import execute_effect

def test_damage():
    game = GameState()
    game.players[1].active = PokemonCard(
        card_id="A",
        supertype="pokemon",
        name="A",
        hp=100,
        current_hp=100,
        types=["normal"],
    )
    effect = {
        "op": "deal_damage",
        "args": {
            "target": { "op": "select", "args": { "who": "opponent", "zone": "active" } },
            "amount": { "op": "const", "value": 30 },
        },
    }
    ctx = EffectContext(0)
    game, _ = execute_effect(effect, game, ctx)
    assert game.players[1].active.current_hp == 70

def test_heal():
    game = GameState()
    game.players[0].active = PokemonCard(
        card_id="A",
        supertype="pokemon",
        name="A",
        hp=100,
        current_hp=50,
        types=["normal"],
    )
    effect = {
        "op": "heal",
        "args": {
            "target": { "op": "select", "args": { "who": "self", "zone": "active" } },
            "amount": { "op": "const", "value": 20 },
        },
    }
    ctx = EffectContext(0)
    game, _ = execute_effect(effect, game, ctx)
    assert game.players[0].active.current_hp == 70

def test_discard_draw():
    game = GameState()
    game.players[0].hand = [BaseCard("H1", "trainer", "H1"), BaseCard("H2", "trainer", "H2"), BaseCard("H3", "trainer", "H3")]
    game.players[0].deck = [BaseCard("D1", "trainer", "D1"), BaseCard("D2", "trainer", "D2"), BaseCard("D3", "trainer", "D3")]
    game.players[0].active = PokemonCard(
        card_id="A",
        supertype="pokemon",
        name="A",
        hp=100,
        current_hp=50,
        types=["normal"],
    )

    effect = {
        "op": "seq",
        "args": {
            "steps": [
                { "op": "discard_from_hand", "args": { "count": { "op": "const", "value": 1 } } },
                { "op": "draw", "args": { "count": { "op": "const", "value": 2 } } },
            ]
        },
    }
    ctx = EffectContext(0)
    game, _ = execute_effect(effect, game, ctx)

    assert len(game.players[0].hand) == 4
    assert [c.card_id for c in game.players[0].discard] == ["H1"]

def test_filters():
    game = GameState()
    p = PokemonCard(
        card_id="X",
        supertype="pokemon",
        name="X",
        hp=100,
        current_hp=100,
        types=["fire"],
    )
    game.players[1].active = p

    effect = {
        "op": "deal_damage",
        "args": {
            "target": {
                "op": "select",
                "args": {
                    "who": "opponent",
                    "zone": "active",
                    "filters": [
                        { "type": "pokemon_type", "value": "fire" }
                    ]
                }
            },
            "amount": { "op": "const", "value": 10 }
        }
    }

    ctx = EffectContext(0)
    game, _ = execute_effect(effect, game, ctx)

    assert p.current_hp == 90
