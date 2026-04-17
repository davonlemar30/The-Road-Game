"""Owned Astari records, species templates, and factories.

The MVP represents an owned Astari as a plain dict so it round-trips through
JSON save/load without custom serializers. Combat still consumes the
`Combatant` dataclass in game.combat.models; owned records are the persistable
truth GP carries between scenes and battles.
"""

from __future__ import annotations

from typing import Any

MURKMIND_SPECIES: dict[str, Any] = {
    "species_id": "murkmind",
    "display_name": "Murkmind",
    "concept": "fog-bound Water pressure Astari",
    "primary_type": "Water",
    "secondary_type": None,
    "zodiac_signature": "Scorpio",
    "base_stats": {
        "max_hp": 25,
        "attack": 10,
        "defense": 11,
        "resolve": 15,
        "speed": 10,
    },
    "starting_moves": ["undertow_hush", "murkveil"],
    "signature_move": "undertow_hush",
    "default_path_alignment": "base",
    "default_bond_label": "Distant",
    "passive": "pressure_drift",
}

SPECIES_TEMPLATES: dict[str, dict[str, Any]] = {
    "murkmind": MURKMIND_SPECIES,
}

MURKMIND_SCENE3_INSTANCE_ID = "murkmind_scene3_001"


def build_owned_murkmind() -> dict[str, Any]:
    """Canonical Scene 3 Lake Ambush Murkmind capture record.

    Locked values per the Chapter 1 canon brief — do not adjust in place.
    """
    return {
        "instance_id": MURKMIND_SCENE3_INSTANCE_ID,
        "species_id": "murkmind",
        "display_name": "Murkmind",
        "level": 4,
        "primary_type": "Water",
        "secondary_type": None,
        "zodiac_signature": "Scorpio",
        "max_hp": 25,
        "current_hp": 25,
        "attack": 10,
        "defense": 11,
        "resolve": 15,
        "speed": 10,
        "moves": ["undertow_hush", "murkveil"],
        "status": None,
        "bond_level": 0,
        "bond_xp": 0,
        "bond_label": "Distant",
        "path_alignment": "base",
        "owner": "player",
        "is_wild": False,
        "will_broken": False,
        "capture_origin": "scene3_lake_ambush",
        "notes": {
            "unstable_first_bond": True,
            "starter_replacement": True,
            "earned_in_rescue": True,
        },
    }


def find_owned(state, instance_id: str) -> dict[str, Any] | None:
    for record in state.owned_astari:
        if record.get("instance_id") == instance_id:
            return record
    return None
