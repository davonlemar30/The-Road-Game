"""ASCII map renderer for ISO Town. Phone-gated — only call after phone_unlocked.

Locations are hidden behind fog-of-war until the player discovers them by visiting
or an NPC reveals them via reveal_location().
"""

from __future__ import annotations

# Short display labels per node
_LABELS: dict[str, str] = {
    "mystic_trail_trailhead": "Trailhead",
    "mystic_trail_outer": "Outer Trail",
    "mystic_trail_split": "Trail Split",
    "mystic_trail_overlook": "Overlook",
    "mystic_trail_safe_hollow": "Safe Hollow",
    "mystic_trail_creek_bend": "Creek Bend",
    "mystic_trail_deep": "Deep Trail",
    "mystic_trail_fog_boundary": "Fog Boundary",
    "keepers_dome":     "Keeper's Dome",
    "fence_line":       "Fence Line",
    "the_archive":      "Archive",
    "the_commons":      "Commons",
    "the_market":       "Market",
    "the_square":       "The Square",
    "foundation_steps": "Fnd. Steps",
    "front_street":     "Front St.",
}

_FOG = "  ???  "


def _label(node_id: str, current: str, discovered: set[str]) -> str:
    if node_id not in discovered:
        return f"[{_FOG}]"
    text = _LABELS[node_id]
    if node_id == current:
        return f"[★{text}]"
    return f"[{text}]"


def render_map(current_node_id: str, discovered: set[str] | None = None) -> str:
    """Return the ASCII map string with fog-of-war applied.

    discovered: set of node_ids the player has visited or had revealed.
    If None, falls back to showing all locations (backwards-compat for saves).
    """
    if discovered is None:
        discovered = set(_LABELS.keys())

    L = {nid: _label(nid, current_node_id, discovered) for nid in _LABELS}

    lines = [
        "  ISO TOWN",
        "  ─────────────────────────────────",
        f"  {L['mystic_trail_trailhead']}──{L['mystic_trail_outer']}──{L['mystic_trail_split']}",
        f"                              │           ├──{L['mystic_trail_overlook']}",
        f"                              │           ├──{L['mystic_trail_creek_bend']}",
        f"                              │           └──{L['mystic_trail_deep']}──{L['mystic_trail_fog_boundary']}",
        f"                              └──{L['mystic_trail_safe_hollow']}",
        "         |",
        f"  {L['keepers_dome']}──{L['fence_line']}",
        "         |              |",
        f"  {L['the_archive']}       {L['the_commons']}──{L['foundation_steps']}",
        "         |              |",
        f"  {L['the_market']}──────{L['the_square']}",
        "                        |",
        f"               {L['front_street']}",
        "  ─────────────────────────────────",
        "  ★ = you are here   [ ??? ] = undiscovered",
    ]
    return "\n".join(lines)
