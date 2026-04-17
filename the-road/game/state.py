"""Runtime game state container."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GameState:
    player_name: str = ""
    current_location: str = "bedroom"
    running: bool = True
    current_objective: str = ""
    money: int = 12
    day: int = 1
    minutes_since_midnight: int = 8 * 60
    inventory: list[str] = field(default_factory=list)
    side_objectives: list[str] = field(default_factory=list)
    journal_notes: list[str] = field(default_factory=list)
    questions_asked: list[str] = field(default_factory=list)
    discovered_locations: list[str] = field(default_factory=list)
    reputation: int = 0
    disposition: int = 0
    relationships: dict[str, int] = field(default_factory=lambda: {"mom": 0, "bob": 0, "nate": 0})
    choice_history: set[str] = field(default_factory=set)
    companions: list[str] = field(default_factory=list)
    flags: dict[str, bool] = field(
        default_factory=lambda: {
            "met_mother": False,
            "mom_talked": False,         # Scene 1 — Mom's monologue delivered
            "permission_granted": False, # Scene 1 — gates house exit
            "in_town": False,            # True after player leaves GP's House
            "dome_entered": False,       # Scene 2 — first arrival at Keeper's Dome
            "codex_given": False,        # Scene 2 — Bob gives GP Nate's parcel
            "codex_delivered": False,    # Scene 3 — Nate's Codex handed off
            "scene3_started": False,
            "scene3_completed": False,
            "met_nate_at_overlook": False,
            "saw_fog_boundary": False,
            "starter_attuned": False,
            "first_rival_battle_done": False,
            "forbidden_trail_unlocked": False,
            "mom_blessing_available": False,  # Scene 4 gate — Bob sends GP home first
            "told_mom_plans": False,     # Scene 4 — Bob sends GP home; Mom gives blessing
            "has_old_phone": False,      # Scene 4 — phone received during Mom's blessing
            "phone_unlocked": False,     # Scene 4+ — phone powered on by player
        }
    )

    @property
    def time_label(self) -> str:
        hour = self.minutes_since_midnight // 60
        minute = self.minutes_since_midnight % 60
        if 5 <= hour < 12:
            block = "Morning"
        elif 12 <= hour < 17:
            block = "Afternoon"
        elif 17 <= hour < 21:
            block = "Evening"
        else:
            block = "Night"
        return f"Day {self.day} • {hour:02d}:{minute:02d} ({block})"
