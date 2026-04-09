"""ASCII map renderer for ISO Town. Phone-gated — only call after phone_unlocked."""

from __future__ import annotations

# Short display labels per node
_LABELS: dict[str, str] = {
    "mystic_trail":     "Mystic Trail",
    "keepers_dome":     "Keeper's Dome",
    "fence_line":       "Fence Line",
    "the_archive":      "Archive",
    "the_commons":      "Commons",
    "the_market":       "Market",
    "the_square":       "The Square",
    "foundation_steps": "Fnd. Steps",
    "front_street":     "Front St.",
}


def _label(node_id: str, current: str) -> str:
    text = _LABELS[node_id]
    if node_id == current:
        return f"[★{text}]"
    return f"[{text}]"


def render_map(current_node_id: str) -> str:
    """Return the ASCII map string with the player's position marked."""
    L = {nid: _label(nid, current_node_id) for nid in _LABELS}

    lines = [
        "  ISO TOWN",
        "  ─────────────────────────────────",
        f"  {L['mystic_trail']}",
        "         |",
        f"  {L['keepers_dome']}──{L['fence_line']}",
        "         |              |",
        f"  {L['the_archive']}       {L['the_commons']}──{L['foundation_steps']}",
        "         |              |",
        f"  {L['the_market']}──────{L['the_square']}",
        "                        |",
        f"               {L['front_street']}",
        "  ─────────────────────────────────",
        "  ★ = you are here",
    ]
    return "\n".join(lines)
