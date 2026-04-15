"""
Renderer — the single choke point between game logic and terminal output.

Renderer.render(view: SceneView) draws one complete frame based on the
current screen mode.  The terminal behaves as distinct zones per mode:

    explore
        ┌──────────────────────────┐
        │  HUD (5 lines, stable)   │
        ├──────────────────────────┤
        │  System-text region      │
        │  (recent output, bounded │
        │   to _MAX_SYSTEM_LINES)  │
        ├──────────────────────────┤
        │  > input prompt          │
        └──────────────────────────┘
        In TTY mode, render() uses cursor-up + erase-to-end to redraw the
        HUD and system region in place.  show_system() appends to a deque
        buffer AND prints immediately so the player sees output without delay.
        In non-TTY mode, output flows sequentially — no cursor tricks.

        show_location() is the primary-content variant of show_system().
        It first clears the system buffer so the room description anchors
        the top of the explore region instead of appending to stale text.
        This separates "where am I" (primary) from "what just happened"
        (secondary transient feedback).

    dialogue
        During structured dialogue sessions, one anchored frame is redrawn
        in-place across beats/choices/hints. Outside sessions, dialogue
        still delegates to the display.py helpers.

    inspect
        Labeled close-up panel for a single object or detail.
        Visually distinct from dialogue (no typewriter; labeled border).
        Supports multi-paragraph text (paragraph breaks on blank lines).
        Blocks for Enter in TTY mode, then returns control to explore.
        In non-TTY mode, prints and continues without blocking.

    log (modal overlay, not a SceneView mode)
        Framed overlay showing recent entries from the persistent log buffer.
        Accessible via the 'log' command.  Reuses the inspect-panel visual
        style for consistency.  All show_system / show_location output is
        captured in the log buffer regardless of TTY mode.
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

        # Persistent log of raw text passed to show_system / show_location.
        # One entry per call, before wrapping.  Used by show_log_view().
        # Larger capacity than _system_buffer — it's a rolling history, not
        # a visual buffer.
        self._log_buffer: deque[str] = deque(maxlen=200)

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
            None for non-interactive modes (explore, inspect),
            selected choice index for dialogue choice frames.
        """
        if view.current_mode == "explore":
            self._render_explore(view)
            return None
        if view.current_mode == "dialogue":
            return self._render_dialogue(view)
        if view.current_mode == "inspect":
            self._render_inspect(view)
            return None
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
        if view.dialogue_lines:
            self.show_dialogue(view.dialogue_lines)
        if view.current_choices:
            selected_idx = self.show_choices(view.choice_prompt_lines, view.current_choices)
        if view.footer_hint:
            self.show_hint(view.footer_hint)
        return selected_idx

    def _dialogue_wrap_rows(self, lines: list[str]) -> list[str]:
        """Wrap dialogue/choice lines to the framed dialogue content width."""
        rows: list[str] = []
        for line in lines:
            if not line or not line.strip():
                rows.append("")
                continue
            rows.extend(
                textwrap.wrap(
                    line.strip(),
                    width=_DIALOGUE_CONTENT_WIDTH,
                    replace_whitespace=True,
                    drop_whitespace=True,
                )
                or [""]
            )
        return rows

    def _dialogue_move_to_anchor(self) -> None:
        """Return cursor to the top of the active dialogue viewport."""
        if not _IS_TTY:
            return
        total = self._dialogue_frame_lines + self._dialogue_tail_lines
        if total > 0:
            sys.stdout.write(f"\033[{total}A\r")
            sys.stdout.write("\033[J")
            sys.stdout.flush()

    def _dialogue_render_frame(self, rows: list[str], footer: str = "") -> None:
        """Render one dialogue viewport frame and track how many lines it consumed."""
        if _IS_TTY:
            self._dialogue_move_to_anchor()

        top = "┌" + "─" * (_DIALOGUE_WIDTH - 2) + "┐"
        bot = "└" + "─" * (_DIALOGUE_WIDTH - 2) + "┘"

        print(top)
        for row in rows:
            print(f"│ {row:<{_DIALOGUE_CONTENT_WIDTH}} │")

        if footer:
            print(f"│ {footer:<{_DIALOGUE_CONTENT_WIDTH}} │")
        print(bot)
        sys.stdout.flush()

        self._dialogue_frame_lines = len(rows) + 3 + (1 if footer else 0)
        self._dialogue_tail_lines = 0

    def _show_session_dialogue(self, lines: list[str]) -> None:
        """Session-aware dialogue render that reuses one anchored viewport."""
        rows = self._dialogue_wrap_rows(lines)
        if not rows:
            rows = [""]
        self._dialogue_render_frame(rows, footer="  ■ Enter")
        self._wait_for_session_ack()

    def _show_session_hint(self, text: str) -> None:
        """Render closing hints inside the active dialogue viewport."""
        rows = self._dialogue_wrap_rows([text]) if text else [""]
        self._dialogue_render_frame(rows, footer="  ■ Enter")
        self._wait_for_session_ack()

    def _wait_for_session_ack(self) -> None:
        """
        Wait for Enter between session dialogue beats in TTY mode.

        This keeps each rendered beat readable before the next in-place redraw.
        input() echoes one newline in TTY mode, so we track that extra tail
        line and include it in the next cursor-up rewind.
        """
        if not _IS_TTY:
            return
        try:
            input()
            self._dialogue_tail_lines = 1
        except (EOFError, KeyboardInterrupt):
            self._dialogue_tail_lines = 0

    def _show_session_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        """Session-aware choice render that reuses the active dialogue viewport."""
        rows = self._dialogue_wrap_rows(prompt_lines)
        if rows:
            rows.append("")

        for i, choice in enumerate(choices, 1):
            rows.extend(self._dialogue_wrap_rows([f"[{i}]  {choice}"]))

        self._dialogue_render_frame(rows, footer="  ◆ Choose")

        while True:
            try:
                raw = input("  > ").strip()
                self._dialogue_tail_lines = 1
                idx = int(raw) - 1
                if 0 <= idx < len(choices):
                    return idx
                print(f"  (Enter a number from 1 to {len(choices)}.)")
                self._dialogue_tail_lines += 1
            except ValueError:
                print(f"  (Enter a number from 1 to {len(choices)}.)")
                self._dialogue_tail_lines += 1

    def _render_inspect(self, view: SceneView) -> None:
        """
        Inspect-mode frame: labeled close-up panel with wrapped detail text.

        Layout (80 chars wide):

            ┌─[ Object Name ]──────────────────────────────────────────────────────────┐
            │                                                                          │
            │  Detailed description text, word-wrapped with a two-space indent.        │
            │                                                                          │
            │  ■ Enter                                                                 │
            └──────────────────────────────────────────────────────────────────────────┘

        Visually distinct from dialogue: no typewriter animation, labeled top
        border, static single-frame render.

        In TTY mode: blocks for Enter before returning so the player can read
        at their own pace.  The next explore render redraws cleanly after.
        In non-TTY mode: prints immediately and returns without blocking.
        """
        _PANEL_WIDTH: int = 80
        # Inner content area between "│ " (2 chars) and " │" (2 chars).
        _CONTENT_WIDTH: int = _PANEL_WIDTH - 4   # 76
        # Wrap text 2 chars narrower than the content area to allow a visual
        # two-space indent that sets inspect detail apart from the border.
        _WRAP_WIDTH: int = _CONTENT_WIDTH - 2    # 74

        target = (view.inspect_target or "Detail").strip()
        text   = (view.inspect_text   or "").strip()

        # ── Borders ───────────────────────────────────────────────────────────
        label = f"[ {target.title()} ]"
        # ┌─{label}{fill dashes}┐ must total exactly _PANEL_WIDTH chars:
        #   1 (┌) + 1 (─) + len(label) + fill + 1 (┐) = 80  →  fill = 77 - len(label)
        fill = max(0, _PANEL_WIDTH - 3 - len(label))
        top  = f"┌─{label}{'─' * fill}┐"
        bot  = "└" + "─" * (_PANEL_WIDTH - 2) + "┘"

        def _row(content: str = "") -> str:
            """One 80-char content row: border + space + padded content + border."""
            return f"│ {content:<{_CONTENT_WIDTH}} │"

        # ── Content rows ──────────────────────────────────────────────────────
        # Support multi-paragraph text for lore/note content: split on blank
        # lines so paragraph breaks render as visual gaps inside the panel.
        paragraphs = [p.strip() for p in text.split("\n\n")] if text else []
        wrapped_rows: list[str] = []
        for i, para in enumerate(paragraphs):
            if not para:
                continue
            if i > 0:
                wrapped_rows.append("")   # blank row between paragraphs
            wrapped_rows.extend(textwrap.wrap(para, width=_WRAP_WIDTH))

        # ── Print panel ───────────────────────────────────────────────────────
        print()          # blank spacer above panel — never overwritten
        print(top)
        print(_row())    # top inner padding
        for row in wrapped_rows:
            print(_row(f"  {row}" if row else ""))
        if view.footer_hint:
            print(_row())
            for row in textwrap.wrap(view.footer_hint.strip(), width=_WRAP_WIDTH):
                print(_row(f"  {row}"))
        print(_row())    # bottom inner padding
        print(_row("  ■ Enter"))
        print(bot)

        if _IS_TTY:
            try:
                input()  # block for Enter; echoes one newline — HUD invalidation handles cleanup
            except (EOFError, KeyboardInterrupt):
                pass

        # Cursor position is now unknown — force a clean explore redraw next frame.
        self._hud_drawn = False
        self._system_buffer.clear()

    def _render_threat(self, view: SceneView) -> None:
        """
        Threat/combat UI shell — presentation scaffold only, no game logic.

        Renders a preview panel showing:
          • optional ASCII portrait (from portraits.py, if defined)
          • threat narrative lines
          • player status snapshot
          • available action choices (display only — no input taken)

        Blocks for Enter in TTY mode, then returns control to explore.
        In non-TTY mode, prints and continues without blocking.

        This is a developer-facing preview while the full combat system is
        designed.  The mode name, panel style, and field layout may change.
        """
        _PANEL_WIDTH: int = 80
        _CONTENT_WIDTH: int = _PANEL_WIDTH - 4   # 76
        _WRAP_WIDTH: int = _CONTENT_WIDTH - 2    # 74

        # ── Portrait (optional) ────────────────────────────────────────────────
        portrait_lines = get_portrait(view.portrait_id) if view.portrait_id else None

        # ── Borders ───────────────────────────────────────────────────────────
        threat_label = view.threat_name or "Unknown Threat"
        label = f"[ Threat: {threat_label} ]"
        fill = max(0, _PANEL_WIDTH - 3 - len(label))
        top  = f"┌─{label}{'─' * fill}┐"
        bot  = "└" + "─" * (_PANEL_WIDTH - 2) + "┘"

        def _row(content: str = "") -> str:
            return f"│ {content:<{_CONTENT_WIDTH}} │"

        def _divider(title: str = "") -> str:
            """Sub-section rule inside the panel."""
            inner = f"  ── {title} " if title else "  "
            dashes = "─" * max(0, _CONTENT_WIDTH - len(inner))
            return _row(f"{inner}{dashes}")

        # ── Print panel ────────────────────────────────────────────────────────
        print()

        # Portrait block above the panel, centered, if art is available.
        if portrait_lines:
            pad = " " * ((_PANEL_WIDTH - len(portrait_lines[0])) // 2)
            for pline in portrait_lines:
                print(f"{pad}{pline}")
            print()

        print(top)
        print(_row())

        # Threat narrative lines.
        for line in (view.threat_lines or []):
            for row in textwrap.wrap(line, width=_WRAP_WIDTH):
                print(_row(f"  {row}"))

        # Player status.
        if view.player_status_lines:
            print(_row())
            print(_divider("Status"))
            for line in view.player_status_lines:
                print(_row(f"  {line}"))

        # Available actions (display only — no input in preview mode).
        if view.combat_actions:
            print(_row())
            print(_divider("Actions"))
            for i, action in enumerate(view.combat_actions, 1):
                print(_row(f"  [{i}]  {action}"))

        print(_row())
        print(_row("  (preview only — no action taken)"))
        print(_row("  ■ Enter"))
        print(bot)

        if _IS_TTY:
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass

        # Cursor position is now unknown — force a clean explore redraw.
        self._hud_drawn = False
        self._system_buffer.clear()

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
        """Render dialogue lines (session-aware when dialogue mode is active)."""
        if self._dialogue_session_active:
            self._show_session_dialogue(lines)
        else:
            _print_dialogue(lines)
            self._hud_drawn = False

    def show_hint(self, text: str) -> None:
        """Render meta hints; in sessions they stay inside the anchored viewport."""
        if self._dialogue_session_active:
            self._show_session_hint(text)
            return

        _print_hint(text)
        if text:
            self._lines_on_screen += 1

    def show_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        """Framed numeric choice box; session-aware when dialogue mode is active."""
        if self._dialogue_session_active:
            return self._show_session_choices(prompt_lines, choices)

        result = _print_choices(prompt_lines, choices)
        self._hud_drawn = False
        return result

    def begin_dialogue_session(self, speaker_name: str) -> None:
        """Open a dialogue session and prepare anchored dialogue viewport state."""
        line_width = 80
        prefix = f"─── {speaker_name} "
        remaining = max(0, line_width - len(prefix))
        print(f"\n{prefix}{'─' * remaining}")

        self._dialogue_session_active = True
        self._dialogue_frame_lines = 0
        self._dialogue_tail_lines = 0
        self._hud_drawn = False

    def end_dialogue_session(self) -> None:
        """Close a dialogue session, leaving one footer rule and resetting state."""
        if self._dialogue_session_active and _IS_TTY:
            self._dialogue_move_to_anchor()

        print("─" * 80)
        self._hud_drawn = False
        self._dialogue_session_active = False
        self._dialogue_frame_lines = 0
        self._dialogue_tail_lines = 0

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

        All non-empty text is also appended to _log_buffer (raw, before
        wrapping) so the 'log' command can show recent history.
        """
        # Log the raw text for the transcript, regardless of TTY mode.
        if text and text.strip():
            self._log_buffer.append(text)

        if not _IS_TTY:
            print(text)
            return

        rows = self._wrap_to_terminal(text)
        for row in rows:
            self._system_buffer.append(row)
            print(row)
            self._lines_on_screen += 1

    def show_location(self, text: str) -> None:
        """
        Display a room or location description as primary explore content.

        Unlike show_system(), this first clears the system buffer so the
        location description anchors the top of the explore display region.
        Subsequent show_system() calls then append navigation feedback below.

        Use this for 'look' output.  Use show_system() for transient
        feedback (travel messages, errors, objective updates, etc.).
        """
        # Clear stale system messages — location description is the new anchor.
        # _lines_on_screen is preserved so the next render() can cursor-up
        # the correct amount and erase the old frame before redrawing.
        self._system_buffer.clear()
        self.show_system(text)

    def show_lines(self, lines: list[str]) -> None:
        """
        Emit a sequence of engine feedback lines, preserving order.
        """
        for line in lines:
            self.show_system(line)

    def show_log_view(self) -> None:
        """
        Show a framed modal overlay of recent exploration log entries.

        Pulls from _log_buffer (raw text, one entry per show_system /
        show_location call) and renders the most recent content inside an
        inspect-style panel.  Blocks for Enter in TTY mode.

        In non-TTY mode, prints a plain list without framing.
        """
        _PANEL_WIDTH: int = 80
        _CONTENT_WIDTH: int = _PANEL_WIDTH - 4   # 76
        _WRAP_WIDTH: int = _CONTENT_WIDTH - 2    # 74
        _MAX_VISIBLE: int = 22                   # max content rows shown

        entries = list(self._log_buffer)

        if not _IS_TTY:
            # Non-TTY: simple unframed output
            print("\n--- Recent Log ---")
            for entry in entries[-20:]:
                if entry and entry.strip():
                    print(entry)
            print("--- End ---\n")
            return

        # Build wrapped rows from all log entries (oldest → newest).
        # Each entry is separated by a blank row so chunks stay readable.
        all_rows: list[str] = []
        for entry in entries:
            if not entry or not entry.strip():
                continue
            for row in textwrap.wrap(entry, width=_WRAP_WIDTH):
                all_rows.append(row)
            all_rows.append("")   # blank separator between log entries

        # Take the most recent rows (tail of the list).
        visible = all_rows[-_MAX_VISIBLE:] if len(all_rows) > _MAX_VISIBLE else all_rows
        # Drop leading blank rows that result from the tail slice.
        while visible and not visible[0].strip():
            visible = visible[1:]

        # ── Panel borders ──────────────────────────────────────────────────────
        label = "[ Recent Log ]"
        fill = max(0, _PANEL_WIDTH - 3 - len(label))
        top  = f"┌─{label}{'─' * fill}┐"
        bot  = "└" + "─" * (_PANEL_WIDTH - 2) + "┘"

        def _row(content: str = "") -> str:
            return f"│ {content:<{_CONTENT_WIDTH}} │"

        # ── Print panel ────────────────────────────────────────────────────────
        print()
        print(top)
        print(_row())
        if not visible:
            print(_row("  (no recent activity)"))
        else:
            for r in visible:
                print(_row(f"  {r}" if r.strip() else ""))
        print(_row())
        print(_row("  ■ Enter"))
        print(bot)

        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

        # Cursor position is now unknown — force a clean explore redraw.
        self._hud_drawn = False
        self._system_buffer.clear()

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
