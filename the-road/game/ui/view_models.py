"""
View models for The Road presentation layer.

A SceneView is the minimal structured description of what the screen should
display at any given moment.  The engine produces it; the Renderer consumes it.

Status (Task 4 — active):
    The engine builds a SceneView each main-loop iteration via _build_view().
    Renderer.render(view) consumes it to draw an anchored HUD in explore mode
    and framed dialogue/choice content in dialogue mode.

Design intent:
    - Engine logic and narrative content never touch terminal output directly.
    - The engine describes WHAT should appear; the Renderer decides HOW.
    - This separation is the prerequisite for a fixed-screen or Rich-style
      renderer in a later phase without rewriting story logic.

Screen modes
────────────
    explore     Default parser mode — HUD visible, command prompt active.
    dialogue    NPC conversation in progress — framed box + choice box.
    inspect     Examining an object or location detail — no HUD overlay needed.
    menu        Main menu, save/load prompts — full-screen, no HUD.
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
    footer_hint         Closing hint printed below the last dialogue beat.
    input_prompt        Prompt string shown before the command cursor.
    system_lines        Transient engine feedback lines (navigation, errors, etc.)
                        In explore mode these are flushed into the system-text
                        region below the HUD.
    """

    current_mode: str = "explore"   # "explore" | "dialogue" | "inspect" | "menu"
    location_name: str = ""
    speaker_name: str = ""
    portrait_id: str = ""           # reserved — not used yet
    dialogue_lines: list[str] = field(default_factory=list)
    current_choices: list[str] = field(default_factory=list)
    choice_prompt_lines: list[str] = field(default_factory=list)
    hud: HudData | None = None
    footer_hint: str = ""
    input_prompt: str = "\n> "
    system_lines: list[str] = field(default_factory=list)
