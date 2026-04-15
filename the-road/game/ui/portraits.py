"""
Terminal-safe portrait placeholders for scene rendering.

Design notes:
    - Portraits are intentionally compact and monochrome.
    - All portraits fit in a small fixed-ish block so they don't overwhelm
      dialogue/combat shells on narrow terminals.
    - Unknown IDs return None so callers can fail gracefully.
"""

from __future__ import annotations

PORTRAITS: dict[str, list[str]] = {
    "npc_mother": [
        "┌──────────────┐",
        "│   .-\"\"-.     │",
        "│  / o  o \\    │",
        "│  |  --  |    │",
        "│  | \\__/ |    │",
        "│  '.___.'     │",
        "│  [Your Mom]  │",
        "└──────────────┘",
    ],
    "npc_bob": [
        "┌──────────────┐",
        "│   ______     │",
        "│  / __  \\     │",
        "│ | |  | |     │",
        "│ | |__| |     │",
        "│  \\____/      │",
        "│ [Keeper Bob] │",
        "└──────────────┘",
    ],
    "npc_audri": [
        "┌──────────────┐",
        "│   .-\"\"-.     │",
        "│  / -  - \\    │",
        "│  |  ..  |    │",
        "│  | \\__/ |    │",
        "│   \\____/     │",
        "│   [Audri]    │",
        "└──────────────┘",
    ],
    "threat_wisp": [
        "┌──────────────┐",
        "│    .--.      │",
        "│  .( oo ).    │",
        "│   /|==|\\     │",
        "│    /  \\      │",
        "│   [WISP]     │",
        "└──────────────┘",
    ],
}


def get_portrait(portrait_id: str) -> list[str] | None:
    """Return portrait lines for portrait_id, or None when missing."""
    if not portrait_id:
        return None
    return PORTRAITS.get(portrait_id)
