"""Early move and stat data for the Combat MVP."""

from __future__ import annotations

from game.combat.models import Combatant, Move

MOVE_DEFS: dict[str, Move] = {
    "steady_strike": Move(
        move_id="steady_strike",
        name="Steady Strike",
        type="Earth",
        power=45,
        accuracy=100,
        text_lines=["Plants feet, then drives a clean hit."],
    ),
    "gust_lance": Move(
        move_id="gust_lance",
        name="Gust Lance",
        type="Air",
        power=55,
        accuracy=95,
        text_lines=["A narrow gust snaps forward like a spear."],
    ),
    "mind_shear": Move(
        move_id="mind_shear",
        name="Mind Shear",
        type="Water",
        power=50,
        accuracy=95,
        effect="Drenched",
        effect_chance=0.3,
        text_lines=["Pressure ripples through the air and bends thought."],
    ),
    "pulse_press": Move(
        move_id="pulse_press",
        name="Pulse Press",
        type="Water",
        power=40,
        accuracy=100,
        effect="Confused",
        effect_chance=0.25,
        text_lines=["The pulse lands off-beat and scrambles focus."],
    ),
    "ember_tap": Move(
        move_id="ember_tap",
        name="Ember Tap",
        type="Fire",
        power=40,
        accuracy=100,
        effect="Burn",
        effect_chance=0.2,
        text_lines=["A quick ember tags exposed seams."],
    ),
    "undertow_hush": Move(
        move_id="undertow_hush",
        name="Undertow Hush",
        type="Water",
        power=10,
        accuracy=95,
        effect="Drenched",
        effect_chance=0.25,
        text_lines=[
            "Murkmind draws the space around the target into a drowning stillness.",
            "The pressure folds inward without warning.",
        ],
    ),
    "murkveil": Move(
        move_id="murkveil",
        name="Murkveil",
        type="Water",
        power=8,
        accuracy=100,
        effect=None,
        effect_chance=None,
        text_lines=[
            "Murkmind casts a low veil of pressure between itself and the target.",
            "The blow lands with damp, quiet weight.",
        ],
    ),
}


CUBE_MODIFIERS: dict[str, float] = {
    "Standard Cube": 1.0,
}


def move(move_id: str) -> Move:
    return MOVE_DEFS[move_id]


def build_player_starter() -> Combatant:
    return Combatant(
        name="Kestrel",
        species_id="aeri-kestrel",
        level=6,
        primary_type="Air",
        secondary_type=None,
        max_hp=28,
        current_hp=28,
        attack=14,
        defense=12,
        resolve=11,
        speed=15,
        moves=[move("steady_strike"), move("gust_lance")],
        status=None,
        owner="player",
        is_wild=False,
        bond_level=1,
        path_alignment="base",
    )


def build_murkmind() -> Combatant:
    return Combatant(
        name="Murkmind",
        species_id="murkmind",
        level=7,
        primary_type="Water",
        secondary_type=None,
        max_hp=32,
        current_hp=32,
        attack=13,
        defense=12,
        resolve=14,
        speed=13,
        moves=[move("mind_shear"), move("pulse_press")],
        status=None,
        owner="enemy",
        is_wild=True,
        bond_level=0,
        path_alignment="base",
    )
