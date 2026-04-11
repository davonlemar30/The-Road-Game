"""Simple, extendable command parser."""
from __future__ import annotations

import re


_FILLER_WORDS = {"to", "the", "at"}


def _normalize_text(text: str) -> str:
    text = text.lower().strip()
    # Normalize curly apostrophes and strip other punctuation to spaces.
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9'\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _strip_leading_fillers(text: str) -> str:
    parts = text.split()
    while parts and parts[0] in _FILLER_WORDS:
        parts.pop(0)
    return " ".join(parts)


def parse_command(raw: str) -> tuple:
    text = _normalize_text(raw or "")
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
    elif verb in {"status", "hub", "player"}:
        verb = "status"
    elif verb in {"shop", "trade"}:
        verb = "browse"

    elif verb == "l":
        verb = "look"

    # ── "talk to / talk with / speak to / speak with" ─────────────────────────
    # Strip the preposition so "talk to mom" and "talk mom" both work.
    if verb == "talk":
        if arg.startswith("to "):
            arg = arg[3:]
        elif arg.startswith("with "):
            arg = arg[5:]
        arg = _strip_leading_fillers(arg)

    # ── "ask about X" (no explicit NPC target) ───────────────────────────────
    # Keep as "about <topic>" and let engine infer a visible NPC if possible.
    if verb == "ask" and arg.startswith("about "):
        return "ask", arg
    if verb == "ask":
        arg = _strip_leading_fillers(arg)

    # ── "tell me about X" / "tell me X" / "tell mom X" → "ask mom X" ─────────
    # Covers: "tell me about nate", "tell mom i'm going", "tell mom plan"
    if verb == "tell":
        remainder = arg
        if remainder.startswith("me "):
            remainder = remainder[3:]
        elif remainder.startswith("mom "):
            remainder = remainder[4:]
        if remainder.startswith("about "):
            remainder = remainder[6:]
        return "ask", "mom " + remainder

    # ── "enter" / "go inside" / "go in" ──────────────────────────────────────
    if verb == "enter":
        return "enter", arg
    if verb == "knock":
        return "enter", arg
    if verb == "open" and arg in {"door", "the door", ""}:
        return "enter", "door"

    if verb == "go":
        if arg.startswith("to "):
            arg = arg[3:]
        arg = _strip_leading_fillers(arg)

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
