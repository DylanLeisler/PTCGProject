from .errors import ExpressionError
from .selectors import resolve_selector

def eval_expr(node, game, ctx):
    op = node["op"]

    if op == "const":
        return node["value"]

    if op == "var":
        name = node["name"]
        if name not in ctx.vars:
            raise ExpressionError(f"Unknown variable: {name}")
        return ctx.vars[name]

    # arithmetic ops
    if op in ("add", "sub", "mul", "div"):
        a = eval_expr(node["args"][0], game, ctx)
        b = eval_expr(node["args"][1], game, ctx)
        if op == "add": return a + b
        if op == "sub": return a - b
        if op == "mul": return a * b
        if op == "div": return a / b

    # comparisons
    if op in ("eq", "lt", "lte", "gt", "gte"):
        a = eval_expr(node["args"][0], game, ctx)
        b = eval_expr(node["args"][1], game, ctx)
        if op == "eq": return a == b
        if op == "lt": return a < b
        if op == "lte": return a <= b
        if op == "gt": return a > b
        if op == "gte": return a >= b

    # boolean logic
    if op in ("and", "or"):
        a = eval_expr(node["args"][0], game, ctx)
        b = eval_expr(node["args"][1], game, ctx)
        return a and b if op == "and" else a or b

    # count selector
    if op == "count":
        sel = node["selector"]
        objs = resolve_selector(sel, game, ctx)
        return len(objs)

    raise ExpressionError(f"Unknown expression op: {op}")
