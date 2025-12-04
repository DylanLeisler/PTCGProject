from .errors import SelectorError

def apply_filter(obj, flt):
    ftype = flt["type"]
    value = flt["value"]

    if ftype == "pokemon_type":
        return hasattr(obj, "types") and value in obj.types

    if ftype == "card_type":
        # TODO: real card objects
        return isinstance(obj, str) and obj.startswith(value)

    if ftype == "hp_at_least":
        return hasattr(obj, "hp") and obj.hp >= value

    if ftype == "hp_at_most":
        return hasattr(obj, "hp") and obj.hp <= value

    if ftype == "and":
        return all(apply_filter(obj, sub) for sub in value)

    raise SelectorError(f"Unknown filter type: {ftype}")
