from .errors import SelectorError
from .filters import apply_filter

def resolve_selector(node, game, ctx):
    args = node["args"]
    who = args["who"]
    zone = args["zone"]
    filters = args.get("filters", [])

    player = (
        game.players[ctx.controller]
        if who == "self"
        else game.players[1 - ctx.controller]
    )

    if zone == "active":
        objs = [player.active] if player.active else []
    elif zone == "bench":
        objs = list(player.bench)
    elif zone == "hand":
        objs = list(player.hand)
    elif zone == "deck":
        objs = list(player.deck)
    elif zone == "discard":
        objs = list(player.discard)
    else:
        raise SelectorError(f"Unsupported zone: {zone}")

    # apply filters
    for flt in filters:
        objs = [o for o in objs if apply_filter(o, flt)]

    return objs

def resolve_single_target(node, game, ctx):
    objs = resolve_selector(node, game, ctx)
    if len(objs) != 1:
        raise SelectorError(f"Expected a single target, got {objs}")
    return objs[0]
