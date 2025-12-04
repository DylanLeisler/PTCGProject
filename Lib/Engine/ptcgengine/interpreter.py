from .expressions import eval_expr
from .primitives import PRIMITIVES
from .errors import InterpreterError
from .utils import trace
from .events import attack_event, GameEvent


def execute_effect(node, game, ctx):
    """
    Executes an effect in a pure functional way and returns:
      (next_state, events: list[GameEvent])

    Existing primitives still operate by mutating the provided game state in place.
    """
    op = node.get("op")
    args = node.get("args", {})

    # Support simple declarative event payloads (non-op style)
    # Example: {"type": "attack", "damage": 30, ...}
    if op is None and "type" in node:
        return _handle_direct_event(node, game, ctx)

    if op is None:
        raise InterpreterError("Effect node missing 'op'")

    trace("EXEC:", op)

    if op == "seq":
        events: list[GameEvent] = []
        for step in args["steps"]:
            game, evts = execute_effect(step, game, ctx)
            events.extend(evts)
        return game, events

    if op == "if":
        cond = eval_expr(args["condition"], game, ctx)
        block = args["then"] if cond else args.get("else", [])
        events: list[GameEvent] = []
        for s in block:
            game, evts = execute_effect(s, game, ctx)
            events.extend(evts)
        return game, events

    if op == "repeat":
        n = eval_expr(args["count"], game, ctx)
        events: list[GameEvent] = []
        for _ in range(n):
            for s in args["body"]:
                game, evts = execute_effect(s, game, ctx)
                events.extend(evts)
        return game, events

    if op in PRIMITIVES:
        game = PRIMITIVES[op](args, game, ctx)
        return game, []

    raise InterpreterError(f"Unknown op: {op}")


def _handle_direct_event(node, game, ctx):
    """Map simple effect dicts to structured GameEvents."""
    ev_type = node.get("type")
    if ev_type == "attack":
        dmg = node.get("damage", 0)
        source = getattr(getattr(ctx, "active", None), "card_id", "unknown")
        target = node.get("target", "unknown")
        ev = attack_event(source=source, target=target, damage=dmg)
        return game, [ev]

    return game, []
