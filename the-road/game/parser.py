"""Simple, extendable command parser."""


def parse_command(raw: str) -> tuple:
    text = (raw or "").strip().lower()
    if not text:
        return "", ""

    parts = text.split(maxsplit=1)
    verb = parts[0]
    arg = parts[1] if len(parts) > 1 else ""

    # ── Verb normalisation ────────────────────────────────────────────────────

    if verb in {"examine", "x", "check"}:
        verb = "inspect"

    elif verb in {"move", "walk"}:
        verb = "go"

    elif verb in {"speak"}:
        verb = "talk"

    elif verb in {"quit", "exit"}:
        verb = "quit"

    elif verb in {"inventory", "inv", "i", "items"}:
        verb = "inventory"

    elif verb == "l":
        verb = "look"

    # ── "talk to / talk with / speak to / speak with" ─────────────────────────
    # Strip the preposition so "talk to mom" and "talk mom" both work.
    if verb == "talk":
        if arg.startswith("to "):
            arg = arg[3:]
        elif arg.startswith("with "):
            arg = arg[5:]

    # ── "ask about X" (no explicit NPC target) → infer mom ───────────────────
    # Covers: "ask about nate", "ask about astari", etc.
    if verb == "ask" and arg.startswith("about "):
        arg = "mom " + arg[6:]

    # ── "tell me about X" / "tell me X" → "ask mom X" ────────────────────────
    # Covers: "tell me about nate", "tell me about astari"
    if verb == "tell":
        remainder = arg
        if remainder.startswith("me "):
            remainder = remainder[3:]
        if remainder.startswith("about "):
            remainder = remainder[6:]
        return "ask", "mom " + remainder

    # ── Directional shortcuts ─────────────────────────────────────────────────
    if verb in {"n", "north"}:
        return "go", "north"
    if verb in {"s", "south"}:
        return "go", "south"
    if verb in {"e", "east"}:
        return "go", "east"
    if verb in {"w", "west"}:
        return "go", "west"

    return verb, arg
