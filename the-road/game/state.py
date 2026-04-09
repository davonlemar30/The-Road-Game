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
            "mom_talked": False,         # Scene 1 — Mom's monologue delivered
            "permission_granted": False, # Scene 1 — gates house exit
            "in_town": False,            # True after player leaves GP's House
            "dome_entered": False,       # Scene 2 — first arrival at Keeper's Dome
            "codex_delivered": False,    # Scene 3 — Nate's Codex handed off
            "told_mom_plans": False,     # Scene 4 — Bob sends GP home; Mom gives blessing
            "has_old_phone": False,      # Scene 4 — phone received during Mom's blessing
            "phone_unlocked": False,     # Scene 4+ — phone powered on by player
        }
    )
