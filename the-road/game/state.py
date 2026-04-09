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
    flags: dict[str, bool] = field(
        default_factory=lambda: {
            "met_mother": False,
            "mom_talked": False,       # main Scene 1 monologue delivered
            "permission_granted": False,
        }
    )
