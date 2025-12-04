from .expressions import eval_expr
from .selectors import resolve_single_target, resolve_selector
from .errors import PrimitiveError

PRIMITIVES = {}

def primitive(name):
    def wrapper(fn):
        PRIMITIVES[name] = fn
        return fn
    return wrapper

@primitive("deal_damage")
def deal_damage(args, game, ctx):
    target = resolve_single_target(args["target"], game, ctx)
    amount = eval_expr(args["amount"], game, ctx)
    # Use current_hp for runtime damage tracking
    target.current_hp -= amount
    return game

@primitive("heal")
def heal(args, game, ctx):
    target = resolve_single_target(args["target"], game, ctx)
    amount = eval_expr(args["amount"], game, ctx)
    target.current_hp += amount
    return game

@primitive("draw")
def draw(args, game, ctx):
    player = game.players[ctx.controller]
    count = eval_expr(args["count"], game, ctx)
    for _ in range(count):
        if player.deck:
            player.hand.append(player.deck.pop())
    return game

@primitive("discard_from_hand")
def discard_from_hand(args, game, ctx):
    player = game.players[ctx.controller]
    count = eval_expr(args["count"], game, ctx)
    for _ in range(min(count, len(player.hand))):
        card = player.hand.pop(0)
        player.discard.append(card)
    return game

@primitive("attach_energy")
def attach_energy(args, game, ctx):
    """
    Generic effect-level attach (e.g. 'attach from discard').
    For the normal once-per-turn attach-from-hand, we use an Action handled in api.step.
    """
    target = resolve_single_target(args["to"], game, ctx)
    energy_card = args["energy_card"]
    target.attached_energies.append(energy_card)
    return game

@primitive("switch_active")
def switch_active(args, game, ctx):
    player = game.players[ctx.controller]
    if not player.bench:
        raise PrimitiveError("No bench Pokémon to switch with.")
    old_active = player.active
    new_active = player.bench.pop(0)
    if old_active:
        player.bench.insert(0, old_active)
    player.active = new_active
    return game

@primitive("move_card")
def move_card(args, game, ctx):
    src = args["src"]
    dst = args["dst"]
    card = args["card"]

    src_list = getattr(game.players[ctx.controller], src)
    dst_list = getattr(game.players[ctx.controller], dst)

    if card not in src_list:
        raise PrimitiveError("Card not in source zone.")

    src_list.remove(card)
    dst_list.append(card)

    return game

@primitive("search_deck")
def search_deck(args, game, ctx):
    player = game.players[ctx.controller]
    sel = resolve_selector(args["selector"], game, ctx)
    maxn = eval_expr(args["max"], game, ctx)
    chosen = sel[:maxn]
    for c in chosen:
        player.deck.remove(c)
        player.hand.append(c)
    return game
