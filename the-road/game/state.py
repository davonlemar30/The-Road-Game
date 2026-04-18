"""Runtime game state container."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class GameState:
    player_name: str = ""
    current_location: str = "bedroom"
    running: bool = True
    current_objective: str = ""
    money: int = 12
    hunger: int = 0
    thirst: int = 0
    fatigue: int = 0
    day: int = 1
    minutes_since_midnight: int = 8 * 60
    inventory: list[str] = field(default_factory=list)
    side_objectives: list[str] = field(default_factory=list)
    journal_notes: list[str] = field(default_factory=list)
    questions_asked: list[str] = field(default_factory=list)
    discovered_locations: list[str] = field(default_factory=list)
    reputation: int = 0
    relationships: dict[str, int] = field(default_factory=lambda: {"mom": 0, "bob": 0, "nate": 0})
    choice_history: set[str] = field(default_factory=set)
    owned_astari: list[dict[str, Any]] = field(default_factory=list)
    active_astari_instance_id: Optional[str] = None
    flags: dict[str, bool] = field(
        default_factory=lambda: {
            "met_mother": False,
            "mom_talked": False,         # Scene 1 — Mom's monologue delivered
            "in_town": False,            # True after player leaves GP's House
            "dome_entered": False,       # Scene 2 — first arrival at Keeper's Dome
            "codex_given": False,        # Scene 2 — Bob gives GP Nate's parcel
            "codex_delivered": False,    # Scene 3 — Nate's Codex handed off
            "scene3_completed": False,
            "scene4_started": False,
            "scene4_completed": False,
            "nate_needs_rest": False,
            "camp_setup_needed": False,
            "water_secured": False,
            "camp_secured": False,
            "campfire_lit": False,
            "camp_kept_dark": False,
            "nate_stable_enough_to_talk": False,
            "nate_recovery_talk_complete": False,
            "survival_system_unlocked": False,
            "survival_system_unlocked_intro_shown": False,
            "camping_unlocked": False,
            "parcel_delivered_to_nate": False,
            "dreamleaf_hint_received": False,
            "jenn_kickback_seeded": False,
            "audri_lake_lore_heard": False,
            "murkmind_helped_find_water": False,
            "murkmind_helped_choose_camp": False,
            "camp_handled_carefully": False,
            "camp_handled_poorly": False,
            "audri_interest_deflected": False,
            "audri_interest_silence": False,
            "audri_interest_admitted": False,
            "dreamleaf_goal_romanticized": False,
            "dreamleaf_goal_self_worth": False,
            "dreamleaf_goal_training": False,
            "saw_fog_boundary": False,
            "starter_attuned": False,
            "first_rival_battle_done": False,
            "forbidden_trail_unlocked": False,
            "mom_blessing_available": False,  # Legacy save compatibility (old Mom-branch gate)
            "told_mom_plans": False,     # Legacy Mom-plan conversation state
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
