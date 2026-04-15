"""
Renderer — the single choke point between game logic and terminal output.

Status (Task 6 — portraits + threat shell scaffold):
    Renderer.render(view: SceneView) draws an anchored HUD followed by a
    bounded system-text region.  The terminal now behaves as three zones:

        ┌──────────────────────────┐
        │  HUD (5 lines, stable)   │
        ├──────────────────────────┤
        │  System-text region      │
        │  (recent output, bounded │
        │   to _MAX_SYSTEM_LINES)  │
        ├──────────────────────────┤
        │  > input prompt          │
        └──────────────────────────┘

    In TTY mode, render() uses cursor-up + erase-to-end to redraw the HUD
    and system region in place.  show_system() appends to a deque buffer
    AND prints immediately so the player sees output without delay.

    In non-TTY mode (CI, piped), output flows sequentially — no cursor
    tricks, no buffering.

    Dialogue mode has a SceneView path and now supports optional portraits.
    Task 6 also adds a renderer-backed "threat" mode shell (UI scaffold only)
    for future combat work.
"""

from __future__ import annotations

import sys
import textwrap
from collections import deque
from shutil import get_terminal_size

from game.display import (
    _IS_TTY,
    menu_choice as _menu_choice,
    print_choices as _print_choices,
    print_dialogue as _print_dialogue,
    print_hint as _print_hint,
    print_status_screen as _print_status_screen,
    print_title_screen as _print_title_screen,
)
from game.ui.portraits import get_portrait
from game.ui.view_models import HudData, SceneView

# ── HUD geometry ─────────────────────────────────────────────────────────────
# The HUD always occupies exactly 5 printed lines:
#   1. blank line
#   2. ═ bar
#   3. info line (name | location | time | gold)
#   4. objective line
#   5. ═ bar
_HUD_HEIGHT: int = 5

# ── System region geometry ───────────────────────────────────────────────────
# Maximum number of visual rows kept in the system-text buffer.
# This bounds the scroll region so it doesn't grow unbounded.
_MAX_SYSTEM_LINES: int = 14
_DIALOGUE_WIDTH: int = 78
_DIALOGUE_CONTENT_WIDTH: int = _DIALOGUE_WIDTH - 4


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
        # Bounded buffer of recent system-text visual rows.
        # Each entry is one terminal line (already wrapped to terminal width).
        self._system_buffer: deque[str] = deque(maxlen=_MAX_SYSTEM_LINES)

        # Total terminal lines on screen since the last render() drew
        # (HUD + system region + input).  Used for cursor-up math.
        self._lines_on_screen: int = 0

        # Whether we have drawn at least one HUD frame this session.
        # The very first frame cannot cursor-up (there is nothing above).
        self._hud_drawn: bool = False

        # Session-aware dialogue viewport state.
        self._dialogue_session_active: bool = False
        self._dialogue_frame_lines: int = 0
        self._dialogue_tail_lines: int = 0

    # ── SceneView dispatch ────────────────────────────────────────────────────

    def render(self, view: SceneView) -> int | None:
        """
        Draw the screen based on a SceneView snapshot.

        Dispatches on view.current_mode.

        Returns:
            None for non-interactive modes (e.g., explore),
            selected choice index for dialogue choice frames.
        """
        if view.current_mode == "explore":
            self._render_explore(view)
            return None
        if view.current_mode == "dialogue":
            return self._render_dialogue(view)
        if view.current_mode == "threat":
            self._render_threat(view)
            return None
        return None

    def _render_dialogue(self, view: SceneView) -> int | None:
        """
        Dialogue-mode frame routed through SceneView state.

        The actual framing/typewriter behavior still lives in display.py.
        This method simply maps SceneView fields onto renderer methods.
        """
        selected_idx: int | None = None
        if view.portrait_id and not self._dialogue_session_active:
            self.show_portrait(view.portrait_id, label=view.speaker_name or "Portrait")
        if view.dialogue_lines:
            if self._dialogue_session_active:
                self._session_show_dialogue(view.dialogue_lines)
            else:
                self.show_dialogue(view.dialogue_lines)
        if view.current_choices:
            if self._dialogue_session_active:
                selected_idx = self._session_show_choices(view.choice_prompt_lines, view.current_choices)
            else:
                selected_idx = self.show_choices(view.choice_prompt_lines, view.current_choices)
        if view.footer_hint:
            if self._dialogue_session_active:
                self._session_show_dialogue([view.footer_hint], marker="■ Enter")
            else:
                self.show_hint(view.footer_hint)
        return selected_idx

    def _render_threat(self, view: SceneView) -> None:
        """
        Threat/combat presentation scaffold.

        This is intentionally UI-only for now: no combat rules, no stateful
        turn system. It simply renders a stable shell the future combat loop
        can target.
        """
        self.invalidate_hud()
        title = view.threat_name or "Unknown Threat"
        bar = "═" * 80
        print(f"\n{bar}")
        print(f"THREAT MODE: {title}")
        print(bar)

        if view.portrait_id:
            self.show_portrait(view.portrait_id, label=title)

        if view.threat_lines:
            print("\nEncounter:")
            for line in view.threat_lines:
                print(f"  {line}")

        if view.player_status_lines:
            print("\nYou:")
            for line in view.player_status_lines:
                print(f"  - {line}")

        if view.combat_actions:
            print("\nActions:")
            for idx, action in enumerate(view.combat_actions, start=1):
                print(f"  {idx}. {action}")

        print("\n(Threat shell only — full combat rules are not implemented yet.)")

    def _render_explore(self, view: SceneView) -> None:
        """
        Explore-mode frame: anchored HUD + bounded system-text region.

        In TTY mode:
          1. Cursor-up over the previous frame (HUD + system text + input).
          2. Erase from cursor to end of screen.
          3. Draw the HUD.
          4. Draw the buffered system lines.
        The result is a stable frame that the player sees in place.

        In non-TTY mode (CI, piped), the HUD is printed sequentially.
        The system buffer is not used — show_system() already printed
        each line as it arrived.
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
        hud_lines = [
            "",             # blank spacer
            bar,
            info,
            f"Objective: {objective}",
            bar,
        ]

        if _IS_TTY and self._hud_drawn:
            # Move cursor back to the top of the previous frame.
            n = self._lines_on_screen
            if n > 0:
                sys.stdout.write(f"\033[{n}A\r")
            # Erase from cursor to end of screen — clears old frame
            # so the redraw starts on a clean canvas.
            sys.stdout.write("\033[J")
            sys.stdout.flush()

        # Draw the HUD.
        for line in hud_lines:
            print(line)

        # Draw the buffered system-text region (TTY only).
        # In non-TTY mode the buffer is not used — text was already printed
        # by show_system() immediately when it arrived.
        system_line_count = 0
        if _IS_TTY:
            for row in self._system_buffer:
                print(row)
                system_line_count += 1

        self._lines_on_screen = _HUD_HEIGHT + system_line_count
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
        self._hud_drawn = False

    # ── Dialogue mode ─────────────────────────────────────────────────────────

    def show_dialogue(self, lines: list[str]) -> None:
        """
        Paginated NPC dialogue box with typewriter animation.

        Dialogue uses its own cursor-up redraw internally (display.py).
        After it finishes, cursor position is unknowable — invalidate.
        """
        _print_dialogue(lines)
        self._hud_drawn = False

    def show_hint(self, text: str) -> None:
        """Single-line meta hint printed outside the dialogue frame."""
        _print_hint(text)
        if text:
            self._lines_on_screen += 1

    def show_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        """Framed numeric choice box; returns selected 0-based index."""
        result = _print_choices(prompt_lines, choices)
        self._hud_drawn = False
        return result

    def show_dialogue_header(self, speaker_name: str, portrait_id: str = "") -> None:
        """Render the opening NPC dialogue rule line."""
        self._dialogue_session_active = True
        self._dialogue_frame_lines = 0
        self._dialogue_tail_lines = 0
        if portrait_id:
            self.show_portrait(portrait_id, label=speaker_name)
        line_width = 80
        prefix = f"─── {speaker_name} "
        remaining = max(0, line_width - len(prefix))
        print(f"\n{prefix}{'─' * remaining}")

    def show_dialogue_footer(self) -> None:
        """Render the closing NPC dialogue rule line."""
        print("─" * 80)
        self._dialogue_session_active = False
        self._dialogue_frame_lines = 0
        self._dialogue_tail_lines = 0

    def show_portrait(self, portrait_id: str, label: str = "Portrait") -> None:
        """
        Print a compact text portrait block.

        Terminal limitation: this is plain mono-text and intentionally small;
        no color/positioning assumptions are made.
        """
        portrait = get_portrait(portrait_id)
        if portrait is None:
            print(f"[{label} portrait unavailable: {portrait_id}]")
            return
        for line in portrait:
            print(line)

    def _dialogue_rows(self, lines: list[str]) -> list[str]:
        rows: list[str] = []
        for line in lines:
            if not line.strip():
                rows.append("")
            else:
                rows.extend(
                    textwrap.wrap(line.strip(), width=_DIALOGUE_CONTENT_WIDTH)
                    or [""]
                )
        return rows or [""]

    def _session_draw_frame(self, rows: list[str], marker: str) -> None:
        if not _IS_TTY:
            print()
            top = "┌" + "─" * (_DIALOGUE_WIDTH - 2) + "┐"
            bot = "└" + "─" * (_DIALOGUE_WIDTH - 2) + "┘"
            print(top)
            for row in rows:
                print(f"│ {row:<{_DIALOGUE_CONTENT_WIDTH}} │")
            print(f"│ {'  ' + marker:<{_DIALOGUE_CONTENT_WIDTH}} │")
            print(bot)
            return

        total_prev = self._dialogue_frame_lines + self._dialogue_tail_lines
        if total_prev > 0:
            sys.stdout.write(f"\033[{total_prev}A\r")
            sys.stdout.write("\033[J")
            sys.stdout.flush()

        top = "┌" + "─" * (_DIALOGUE_WIDTH - 2) + "┐"
        bot = "└" + "─" * (_DIALOGUE_WIDTH - 2) + "┘"
        frame_lines = [top]
        frame_lines.extend(f"│ {row:<{_DIALOGUE_CONTENT_WIDTH}} │" for row in rows)
        frame_lines.append(f"│ {'  ' + marker:<{_DIALOGUE_CONTENT_WIDTH}} │")
        frame_lines.append(bot)
        for line in frame_lines:
            print(line)
        self._dialogue_frame_lines = len(frame_lines)
        self._dialogue_tail_lines = 0

    def _session_show_dialogue(self, lines: list[str], marker: str = "■ Enter") -> None:
        rows = self._dialogue_rows(lines)
        self._session_draw_frame(rows, marker=marker)

        if not _IS_TTY:
            return
        input("  > ")
        self._dialogue_tail_lines = 1

    def _session_show_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        rows = self._dialogue_rows(prompt_lines)
        if rows and rows != [""]:
            rows.append("")
        for i, choice in enumerate(choices, 1):
            rows.extend(self._dialogue_rows([f"[{i}]  {choice}"]))

        self._session_draw_frame(rows, marker="◆ Choose")

        tail = 0
        while True:
            raw = input("  > ").strip()
            tail += 1
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(choices):
                    self._dialogue_tail_lines = tail
                    return idx
            except ValueError:
                pass
            print(f"  (Enter a number from 1 to {len(choices)}.)")
            tail += 1

    # ── System / explore mode ─────────────────────────────────────────────────

    def _wrap_to_terminal(self, text: str) -> list[str]:
        """
        Split a text block into visual rows that fit the terminal width.

        Handles embedded newlines, blank lines, and long lines that need
        wrapping.  Returns a list of strings, each representing one
        terminal row.
        """
        cols = get_terminal_size(fallback=(80, 24)).columns
        rows: list[str] = []
        for line in text.split("\n"):
            if not line.strip():
                rows.append("")
            else:
                rows.extend(
                    textwrap.wrap(line, width=cols, replace_whitespace=False)
                    or [""]
                )
        return rows

    def show_system(self, text: str) -> None:
        """
        Emit one transient engine feedback line or block.

        TTY mode:
          Wraps the text to terminal width, appends visual rows to the
          bounded system buffer, and prints them immediately so the player
          sees the response without delay.  The next render() will redraw
          both the HUD and the buffer contents in place.

        Non-TTY mode:
          Prints immediately — no buffering needed since there are no
          cursor tricks to erase previous output.
        """
        if not _IS_TTY:
            print(text)
            return

        rows = self._wrap_to_terminal(text)
        for row in rows:
            self._system_buffer.append(row)
            print(row)
            self._lines_on_screen += 1

    def show_lines(self, lines: list[str]) -> None:
        """
        Emit a sequence of engine feedback lines, preserving order.
        """
        for line in lines:
            self.show_system(line)

    # ── Input ─────────────────────────────────────────────────────────────────

    def get_input(self, prompt: str = "\n> ") -> str:
        """
        Block for the main command prompt input.

        The prompt itself may contain newlines (e.g. the default "\\n> "
        starts with a blank line).  After the user presses Enter, the
        cursor moves to a new line.  Total terminal lines consumed:
          prompt newlines + 1 (the input line itself).
        """
        result = input(prompt)
        self._lines_on_screen += prompt.count("\n") + 1
        return result

    def get_text_input(self, prompt: str) -> str:
        """
        Block for free-text input (e.g. name entry at game start).

        Separate from get_input() so a future renderer can style these
        differently from the command-line cursor.
        """
        result = input(prompt)
        self._lines_on_screen += prompt.count("\n") + 1
        return result

    # ── Anchoring control ─────────────────────────────────────────────────────

    def invalidate_hud(self) -> None:
        """
        Force the next render() to draw the HUD without cursor-up.

        Call this after any operation that disrupts the terminal's line
        position relative to the HUD (dialogue sessions, full-screen
        overlays, status screen, etc.).

        Also clears the system buffer — after a dialogue session the
        previous explore-mode output is no longer contextually relevant
        and redrawing stale lines below a fresh HUD would be confusing.
        """
        self._hud_drawn = False
        self._system_buffer.clear()
        self._dialogue_session_active = False
        self._dialogue_frame_lines = 0
        self._dialogue_tail_lines = 0
