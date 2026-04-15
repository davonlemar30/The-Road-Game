from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HudData:
    """Extracted HUD fields so the renderer doesn't need direct GameState access."""

    player_name: str = ""
    location_name: str = ""
    time_label: str = ""
    money: int = 0
    objective: str = ""
    reputation: int = 0
    disposition: int = 0


@dataclass
class SidebarSection:
    """Small labeled block for the right sidebar."""

    title: str
    lines: list[str] = field(default_factory=list)


@dataclass
class JournalView:
    """Snapshot of objective and narrative note data for the journal screen."""

    main_objective: str = ""
    side_objectives: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class SceneView:
    """Renderer-facing snapshot for one frame."""

    current_mode: str = "explore"
    location_name: str = ""
    speaker_name: str = ""
    portrait_id: str = ""

    hud: HudData | None = None
    sidebar_sections: list[SidebarSection] = field(default_factory=list)

    main_lines: list[str] = field(default_factory=list)
    dialogue_lines: list[str] = field(default_factory=list)
    current_choices: list[str] = field(default_factory=list)
    choice_prompt_lines: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)

    footer_hint: str = ""
    input_prompt: str = "> "
    system_lines: list[str] = field(default_factory=list)

    threat_name: str = ""
    threat_lines: list[str] = field(default_factory=list)
    player_status_lines: list[str] = field(default_factory=list)
    combat_actions: list[str] = field(default_factory=list)

    inspect_target: str = ""
    inspect_text: str = ""
    journal: JournalView | None = None
