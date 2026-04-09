"""Runtime game state container."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GameState:
    player_name: str = ""
    current_location: str = "bedroom"
    running: bool = True
    current_objective: str = ""
    inventory: list[str] = field(default_factory=list)
    questions_asked: list[str] = field(default_factory=list)
    discovered_locations: list[str] = field(default_factory=list)
    flags: dict[str, bool] = field(
        default_factory=lambda: {
            "met_mother": False,
            "mom_talked": False,       # main Scene 1 monologue delivered
            "told_mom_plans": False,   # player told mom they're going (triggers phone + permission)
            "permission_granted": False,
            "in_town": False,          # True after player leaves GP's House
            "has_old_phone": False,    # True after Mom hands over phone during blessing
            "phone_unlocked": False,   # True after player uses phone for first time
            "dome_entered": False,     # True on first arrival at Keeper's Dome
        }
    )
