"""
Renderer — the single choke point between game logic and terminal output.

Status (Task 3 — active):
    Renderer.render(view: SceneView) is now the primary entry point for the
    main game loop.  In explore mode it draws an anchored HUD: the cursor is
    repositioned before each redraw so the HUD occupies a stable visual region
    at the top of the output rather than scrolling past.

    System text (show_system / show_lines) still prints immediately so the
    player sees command responses without delay.  The line-counting mechanism
    (_lines_since_hud) lets the next render() call know exactly how far to
    move the cursor back.

    Dialogue, menu, and inspect modes remain compatibility paths — they use
    the direct show_* methods and bypass the SceneView pipeline for now.

TTY anchoring strategy:
    display.py already has _IS_TTY, _cursor_up(), and ANSI line-erase.
    We reuse the same techniques here:
      1. After drawing the HUD, record _lines_since_hud = HUD height.
      2. Every show_system() / show_lines() call increments the counter.
      3. get_input() adds 2 (the prompt line + the user's typed response).
      4. On the next render(), cursor-up by _lines_since_hud, erase to
         end-of-screen (\033[J), then redraw the HUD.
    In non-TTY mode, the cursor tricks are skipped — output flows
    sequentially as before.  The game works identically; it just scrolls.

Why not Textual (for now):
    display.py already implements stationary-frame TTY redraws, termios raw
    input, typewriter animation, and multi-environment fallbacks (CI / piped).
    The anchored-HUD approach here builds on that same ANSI foundation with
    minimal added complexity.
"""

from __future__ import annotations

import sys

from game.display import (
    _IS_TTY,
    menu_choice as _menu_choice,
    print_choices as _print_choices,
    print_dialogue as _print_dialogue,
    print_hint as _print_hint,
    print_status_screen as _print_status_screen,
    print_title_screen as _print_title_screen,
)

# Note: print_hud is no longer imported — the HUD is now rendered directly
# by _render_explore() using HudData from the SceneView, with the same
# visual format but anchored via cursor positioning.
from game.ui.view_models import HudData, SceneView

# ── HUD geometry ─────────────────────────────────────────────────────────────
# print_hud emits exactly 5 lines:
#   1. blank line (print())
#   2. ═ bar
#   3. info line
#   4. objective line
#   5. ═ bar
_HUD_HEIGHT: int = 5


class Renderer:
    """
    Wraps all terminal output for The Road.

    GameEngine holds one instance (self.renderer) and calls these methods
    instead of calling print(), input(), or display.py functions directly.

    The primary entry point for the main loop is render(view: SceneView),
    which dispatches on view.current_mode.  Direct show_* methods remain
    available for compatibility paths (dialogue sessions, menu screens).
    """

    def __init__(self) -> None:
        # How many terminal lines have been printed since the last HUD draw.
        # Used by the TTY anchoring logic to know how far to cursor-up.
        self._lines_since_hud: int = 0
        # Whether we have drawn at least one HUD frame this session.
        # The very first frame cannot cursor-up (there is nothing above).
        self._hud_drawn: bool = False

    # ── SceneView dispatch ────────────────────────────────────────────────────

    def render(self, view: SceneView) -> None:
        """
        Draw the screen based on a SceneView snapshot.

        Dispatches on view.current_mode.  Currently only 'explore' has a
        real implementation; other modes are stubs that will be filled in
        by future tasks.
        """
        if view.current_mode == "explore":
            self._render_explore(view)
        else:
            # Compatibility: other modes don't use SceneView rendering yet.
            # Dialogue, menu, and inspect continue to use direct show_* calls.
            pass

    def _render_explore(self, view: SceneView) -> None:
        """
        Explore-mode frame: anchored HUD + system text region.

        In TTY mode, the HUD is redrawn in-place by moving the cursor back
        over the previous HUD + all system text emitted since.  This creates
        a stable visual region at the top of the terminal output.

        In non-TTY mode (CI, piped), the HUD is simply printed sequentially.
        """
        if view.hud is None:
            return

        hud = view.hud

        # Build the HUD text lines (same visual shape as display.print_hud).
        objective = hud.objective or "No objective"
        if len(objective) > 42:
            objective = objective[:39] + "..."
        bar = "═" * 80
        info = (
            f"{hud.player_name or 'Unknown'}  |  {hud.location_name}  |  "
            f"{hud.time_label}  |  Gold: {hud.money}"
        )
        hud_text = [
            "",             # blank spacer
            bar,
            info,
            f"Objective: {objective}",
            bar,
        ]

        if _IS_TTY and self._hud_drawn:
            # Move cursor back to the top of the previous HUD frame.
            n = self._lines_since_hud
            if n > 0:
                sys.stdout.write(f"\033[{n}A\r")
            # Erase from cursor to end of screen — clears old HUD + old
            # system text so the redraw starts on a clean canvas.
            sys.stdout.write("\033[J")
            sys.stdout.flush()

        # Draw the HUD lines.
        for line in hud_text:
            print(line)

        self._lines_since_hud = _HUD_HEIGHT
        self._hud_drawn = True

    # ── Structural screens ────────────────────────────────────────────────────

    def show_title(self) -> None:
        """Full-screen title / splash."""
        _print_title_screen()

    def show_menu(self, prompt: str, options: list[str]) -> int:
        """Numbered menu; returns selected 0-based index."""
        return _menu_choice(prompt, options)

    def show_status(self, state, location_name: str) -> None:
        """Player status hub (opened by 'status' command)."""
        _print_status_screen(state, location_name)
        # Status screen outputs ~15+ lines; we don't know the exact count
        # so invalidate the HUD position to force a clean redraw next frame.
        self._hud_drawn = False

    # ── Dialogue mode ─────────────────────────────────────────────────────────

    def show_dialogue(self, lines: list[str]) -> None:
        """
        Paginated NPC dialogue box with typewriter animation.

        Dialogue boxes use their own cursor-up redraw internally (display.py).
        After a dialogue session the cursor position relative to the HUD is
        unknowable, so we invalidate _hud_drawn to force a clean redraw.
        """
        _print_dialogue(lines)
        # Dialogue's internal cursor tricks break our line count.
        self._hud_drawn = False

    def show_hint(self, text: str) -> None:
        """Single-line meta hint printed outside the dialogue frame."""
        _print_hint(text)
        if text:
            self._lines_since_hud += 1

    def show_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        """
        Framed numeric choice box; returns selected 0-based index.
        choices.run_scene_choice calls display.print_choices directly — unchanged.
        """
        result = _print_choices(prompt_lines, choices)
        # Choice box has variable height + input; invalidate.
        self._hud_drawn = False
        return result

    # ── System / explore mode ─────────────────────────────────────────────────

    def show_system(self, text: str) -> None:
        """
        Emit one transient engine feedback line or block.

        Prints immediately so the player sees the response without delay.
        Increments the line counter so the next render() call can cursor-up
        the correct distance to redraw the HUD in place.
        """
        print(text)
        # Count how many terminal lines this text occupies.
        # Each print() adds 1 for the trailing newline; embedded \n adds more.
        self._lines_since_hud += 1 + text.count("\n")

    def show_lines(self, lines: list[str]) -> None:
        """
        Emit a sequence of engine feedback lines, preserving order.

        Each element is printed as its own line.  The line counter is
        updated for each.
        """
        for line in lines:
            print(line)
            self._lines_since_hud += 1 + line.count("\n")

    # ── Input ─────────────────────────────────────────────────────────────────

    def get_input(self, prompt: str = "\n> ") -> str:
        """
        Block for the main command prompt input.

        The prompt itself occupies terminal lines (the leading \\n in the
        default prompt creates a blank line, then "> " is on the next line).
        The user's typed response stays on that same line, but when they press
        Enter the cursor moves to a new line.  So the total is:
          prompt newlines + 1 (the input line itself)
        """
        result = input(prompt)
        self._lines_since_hud += prompt.count("\n") + 1
        return result

    def get_text_input(self, prompt: str) -> str:
        """
        Block for free-text input (e.g. name entry at game start).

        Separate from get_input() so a future renderer can style or position
        these prompts differently from the command-line cursor.
        """
        result = input(prompt)
        self._lines_since_hud += prompt.count("\n") + 1
        return result

    # ── Anchoring control ─────────────────────────────────────────────────────

    def invalidate_hud(self) -> None:
        """
        Force the next render() to draw the HUD without cursor-up.

        Call this after any operation that disrupts the terminal's line
        position relative to the HUD (dialogue sessions, full-screen
        overlays, status screen, etc.).
        """
        self._hud_drawn = False
