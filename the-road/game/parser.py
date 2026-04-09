"""Simple, extendable command parser."""


def parse_command(raw: str) -> tuple[str, str]:
    text = (raw or "").strip().lower()
    if not text:
        return "", ""

    parts = text.split(maxsplit=1)
    verb = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    # Verb synonyms
    if verb in {"examine", "x", "look at"}:
        verb = "inspect"
    elif verb in {"move", "walk"}:
        verb = "go"
    elif verb in {"speak", "talk to"}:
        verb = "talk"
    elif verb in {"quit", "exit"}:
        verb = "quit"
    elif verb in {"inventory", "inv", "i", "items"}:
        verb = "inventory"
    elif verb == "l":
        verb = "look"

    # Directional shortcuts
    if verb in {"n", "north"}:
        return "go", "north"
    if verb in {"s", "south"}:
        return "go", "south"
    if verb in {"e", "east"}:
        return "go", "east"
    if verb in {"w", "west"}:
        return "go", "west"

    return verb, arg
