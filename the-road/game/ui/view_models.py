"""
View models for The Road presentation layer.

A SceneView is the minimal structured description of what the screen should
display at any given moment.  The engine produces it; the Renderer consumes it.

Design intent:
    - Engine logic and narrative content never touch terminal output directly.
    - The engine describes WHAT should appear; the Renderer decides HOW.
    - This separation is the prerequisite for a fixed-screen or Rich-style
      renderer in a later phase without rewriting story logic.

Screen modes
────────────
    explore     Default parser mode — HUD visible, command prompt active.
    dialogue    NPC conversation in progress — framed box + choice box.
    inspect     Close-up view of one object or detail — labeled panel, no HUD.
    menu        Main menu, save/load prompts — full-screen, no HUD.
    threat      Combat/threat UI shell (presentation scaffold only).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HudData:
    """Extracted HUD fields so the renderer doesn't need to reach into GameState."""
    player_name: str = ""
    location_name: str = ""
    time_label: str = ""
    money: int = 0
    objective: str = ""


@dataclass
class SceneView:
    """
    Snapshot of everything the renderer needs to draw one frame.

    Fields
    ──────
    current_mode        Active screen mode (see module docstring).
    location_name       Human-readable name for the current location.
    speaker_name        NPC name shown in the dialogue header (dialogue mode).
    portrait_id         Reserved for a future ASCII portrait lookup key.
    dialogue_lines      Lines to pass to print_dialogue / Renderer.show_dialogue.
    current_choices     Option strings for the choice box (dialogue mode).
    choice_prompt_lines Prompt text lines shown above choices (dialogue mode).
    hud                 Extracted HUD data; None suppresses HUD redraw.
    footer_hint         Closing hint printed below the last dialogue beat,
                        or optional context line inside the inspect panel.
    input_prompt        Prompt string shown before the command cursor.
    system_lines        Transient engine feedback lines (navigation, errors, etc.)
                        In explore mode these are flushed into the system-text
                        region below the HUD.
    inspect_target      Name of the object being examined (inspect mode).
                        Shown in the panel's labeled top border.
    inspect_text        Detailed description text for the inspected object.
    """

    current_mode: str = "explore"   # "explore" | "dialogue" | "inspect" | "menu" | "threat"
    location_name: str = ""
    speaker_name: str = ""
    portrait_id: str = ""           # reserved — not used yet
    dialogue_lines: list[str] = field(default_factory=list)
    current_choices: list[str] = field(default_factory=list)
    choice_prompt_lines: list[str] = field(default_factory=list)
    hud: HudData | None = None
    footer_hint: str = ""
    threat_name: str = ""
    threat_lines: list[str] = field(default_factory=list)
    player_status_lines: list[str] = field(default_factory=list)
    combat_actions: list[str] = field(default_factory=list)
    input_prompt: str = "\n> "
    system_lines: list[str] = field(default_factory=list)
    inspect_target: str = ""        # inspect mode: object label for panel header
    inspect_text: str = ""          # inspect mode: detail description text
