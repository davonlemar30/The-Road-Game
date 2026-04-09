"""Runtime game state container."""

from dataclasses import dataclass, field


@dataclass
class GameState:
    player_name: str = ""
    current_location: str = "bedroom"
    running: bool = True
    current_objective: str = ""
    inventory: list[str] = field(default_factory=list)
    flags: dict[str, bool] = field(
        default_factory=lambda: {
            "met_mother": False,
            "heard_astari_warning": False,
            "objective_find_nate_added": False,
            "dialogue_completed": False,
            "permission_granted": False,
        }
    )
