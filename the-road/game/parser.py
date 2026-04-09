"""Simple, extendable command parser."""


def parse_command(raw: str) -> tuple[str, str]:
    text = (raw or "").strip().lower()
    if not text:
        return "", ""

    parts = text.split(maxsplit=1)
    verb = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    if verb in {"examine", "x"}:
        verb = "inspect"
    elif verb in {"move", "walk"}:
        verb = "go"
    elif verb in {"speak"}:
        verb = "talk"
    elif verb in {"quit", "exit"}:
        verb = "quit"

    if verb in {"n", "north"}:
        return "go", "north"
    if verb in {"s", "south"}:
        return "go", "south"
    if verb in {"e", "east"}:
        return "go", "east"
    if verb in {"w", "west"}:
        return "go", "west"

    return verb, arg
