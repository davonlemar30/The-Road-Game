"""
Terminal display utilities for The Road.

Separates NPC dialogue from system text with a framed, paginated dialogue box.

Architecture:
  - Dialogue renders inside a fixed-height ASCII frame (_BOX_TOTAL_LINES tall).
  - Content is paginated into _PAGE_LINES rows per page.
  - In TTY + termios mode, subsequent pages overwrite the previous box in-place
    using an ANSI cursor-up sequence, creating a stationary-frame illusion.
  - In TTY mode, each content row animates character-by-character (typewriter).
    Border lines, padding rows, and footer lines are printed instantly.
  - Without termios (Windows / unusual envs), falls back to input() with a +1
    cursor offset to compensate for the echoed newline.
  - In non-TTY mode (CI, piped input, tests), all pages print sequentially with
    no cursor movement, no animation, and no blocking — auto-advance.
  - Hint/meta lines bypass the frame and print below the last page.
"""

from __future__ import annotations

import sys
import textwrap
import time
from shutil import get_terminal_size

# ── Box geometry (fixed at import — must never vary at runtime) ───────────────

_BOX_WIDTH: int = 78
_CONTENT_WIDTH: int = _BOX_WIDTH - 4   # "│ " (2 chars) + content + " │" (2 chars)
_PAGE_LINES: int = 3                   # visible content rows per page

# The box always occupies exactly this many printed lines, regardless of how
# much content is on a given page.  Padding rows fill unused content slots.
#
#   1  ── top border
#   _PAGE_LINES  ── content rows (always padded to this count)
#   1  ── footer  (▼ / ■ Enter)
#   1  ── bottom border
#   ──────────────────────
#   _PAGE_LINES + 3  total   (= 6)
#
# This constant is the contract that makes cursor-up redraws safe: every
# overwrite moves the cursor up exactly this many lines.
_BOX_TOTAL_LINES: int = _PAGE_LINES + 3

# ── Typewriter timing ─────────────────────────────────────────────────────────

_CHAR_DELAY: float = 0.018       # seconds between characters  (~55 chars/sec)
_SENTENCE_PAUSE: float = 0.110   # extra pause after sentence-ending punctuation

# Characters that trigger the sentence pause.
# Em dash (—) is included because dialogue uses it for natural speech breaks.
_PAUSE_CHARS: frozenset = frozenset(".!?—…")

# ── Capability detection (once at import, never re-evaluated) ─────────────────

# Cursor movement and animation only make sense when both streams are real TTYs.
_IS_TTY: bool = sys.stdin.isatty() and sys.stdout.isatty()

# termios lets us read a single keypress with no echo so the cursor stays put.
# Without it we fall back to input(), which echoes a newline (see offset below).
try:
    import termios as _termios
    import tty as _tty
    _HAS_TERMIOS: bool = True
except ImportError:
    _HAS_TERMIOS = False


# ── Internal: text processing ─────────────────────────────────────────────────

def _wrap_for_box(line: str) -> list[str]:
    """Wrap one script line into fixed-width visual rows."""
    if not line.strip():
        return [""]
    return textwrap.wrap(
        line.strip(),
        width=_CONTENT_WIDTH,
        replace_whitespace=True,
        drop_whitespace=True,
    )


def _paginate(rows: list[str], page_size: int = _PAGE_LINES) -> list[list[str]]:
    """Chunk visual rows into fixed-size pages."""
    if not rows:
        return [[]]
    return [rows[i : i + page_size] for i in range(0, len(rows), page_size)]


# ── Internal: line-level output helpers ──────────────────────────────────────

def _print_line(text: str) -> None:
    """
    Print one full line.

    In TTY mode: erases the current terminal line before writing so old
    content from a previous page never bleeds through on a cursor-up redraw.
    In non-TTY mode: plain print with no escape codes (safe for log capture).
    """
    if _IS_TTY:
        sys.stdout.write(f"\033[2K\r{text}\n")
    else:
        print(text)


def _typewrite_row(text: str) -> None:
    """
    Print one content row inside the box with character-by-character animation.

    Only called in TTY mode on rows that carry actual text.
    Erases the current line first (\033[2K\r) so a cursor-up overwrite never
    leaves stale characters from the previous page.

    Timing:
      _CHAR_DELAY      — base delay between characters
      _SENTENCE_PAUSE  — extra pause after punctuation in _PAUSE_CHARS,
                         mimicking the natural rhythm of spoken dialogue
    """
    # Erase the current terminal line and return to column 0 before typing.
    sys.stdout.write("\033[2K\r│ ")
    sys.stdout.flush()

    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        pause = _SENTENCE_PAUSE if ch in _PAUSE_CHARS else _CHAR_DELAY
        time.sleep(pause)

    # Pad the remaining width and close the row — appears instantly after
    # the last character so the right border is always aligned.
    sys.stdout.write(" " * (_CONTENT_WIDTH - len(text)) + " │\n")
    sys.stdout.flush()


# ── Internal: rendering ───────────────────────────────────────────────────────

def _render_box(rows: list[str], has_next: bool) -> None:
    """
    Print one full dialogue page inside the ASCII frame.

    Always emits exactly _BOX_TOTAL_LINES lines.  Pages with fewer content
    rows than _PAGE_LINES get blank padding rows so the frame height is stable.
    Stable height is the prerequisite for correct cursor-up math.

    In TTY mode: each non-empty content row is animated via _typewrite_row,
    which also handles line-clearing for clean overwrites.
    In non-TTY mode: all rows print instantly via _print_line.
    """
    marker = "▼" if has_next else "■"
    top = "┌" + "─" * (_BOX_WIDTH - 2) + "┐"
    bot = "└" + "─" * (_BOX_WIDTH - 2) + "┘"

    _print_line(top)

    for row in rows:
        if _IS_TTY and row.strip():
            _typewrite_row(row)                              # animated
        else:
            _print_line(f"│ {row:<{_CONTENT_WIDTH}} │")    # instant (blank/non-TTY)

    # Pad to exactly _PAGE_LINES content rows — keeps _BOX_TOTAL_LINES constant.
    for _ in range(max(0, _PAGE_LINES - len(rows))):
        _print_line(f"│ {'':<{_CONTENT_WIDTH}} │")

    _print_line(f"│ {'  ' + marker + ' Enter':<{_CONTENT_WIDTH}} │")
    _print_line(bot)
    sys.stdout.flush()


# ── Internal: cursor control ──────────────────────────────────────────────────

def _cursor_up(n: int) -> None:
    """
    Move the terminal cursor up n lines and reset to column 0.

    ANSI CSI A (\\033[nA) moves up n rows but preserves the column.
    The trailing \\r resets to column 0 so subsequent write calls fully
    overwrite each line from the left edge.
    """
    sys.stdout.write(f"\033[{n}A\r")
    sys.stdout.flush()


# ── Internal: input (wait for Enter) ─────────────────────────────────────────

def _read_enter_raw() -> None:
    """
    Block until the player presses any key, with zero terminal output.

    Puts stdin into raw mode so the keypress is not echoed and produces no
    newline.  After this function returns, the cursor has not moved — it
    stays on the line immediately below the box's bottom border.

    That is why the cursor-up offset for the next page is exactly
    _BOX_TOTAL_LINES (not _BOX_TOTAL_LINES + 1).

    Raises KeyboardInterrupt if Ctrl-C is pressed (raw mode would otherwise
    deliver it as a plain \\x03 character rather than raising the signal).
    """
    fd = sys.stdin.fileno()
    old_settings = _termios.tcgetattr(fd)
    try:
        _tty.setraw(fd)
        ch = sys.stdin.read(1)   # block until exactly one character arrives
    finally:
        # Always restore terminal state, even if an exception is raised.
        _termios.tcsetattr(fd, _termios.TCSADRAIN, old_settings)

    if ch == "\x03":
        raise KeyboardInterrupt


# ── Public API ────────────────────────────────────────────────────────────────

def print_dialogue(lines: list) -> None:
    """
    Display a block of NPC lines in a paginated, stationary dialogue frame.

    Behaviour by environment
    ────────────────────────
    TTY + termios   Content animates character-by-character; silent Enter
                    read keeps cursor in place; next page overwrites by moving
                    up exactly _BOX_TOTAL_LINES lines.

    TTY, no termios Content still animates; input() echoes \\n so the cursor
                    moves one extra line down; next page moves up
                    _BOX_TOTAL_LINES + 1 to compensate.

    Non-TTY         Pages print sequentially, instantly, with no blocking.
                    Safe for log capture, CI, and redirected output.

    Lines beginning with "(" or "\\n" are treated as hints/passthrough and
    printed below the final page, outside the frame, unchanged.
    """
    print()   # one blank spacer above the box; printed once, never overwritten

    passthrough_lines: list[str] = []
    visual_rows: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            visual_rows.append("")
            continue
        if stripped.startswith("(") or stripped.startswith("\n"):
            passthrough_lines.append(line)
            continue
        visual_rows.extend(_wrap_for_box(line))

    pages = _paginate(visual_rows)

    for idx, page in enumerate(pages):
        has_next = idx < len(pages) - 1

        if idx > 0 and _IS_TTY:
            # ── Cursor-up redraw ─────────────────────────────────────────────
            #
            # Move the cursor back to the top-left corner of the box so the
            # upcoming _render_box() calls overwrite it in-place.
            #
            # After _read_enter_raw() (termios, no echo):
            #   Cursor is exactly _BOX_TOTAL_LINES below the top border.
            #   → move up _BOX_TOTAL_LINES.
            #
            # After input() (no termios, echoes \\n):
            #   input() moved the cursor one extra line down.
            #   → move up _BOX_TOTAL_LINES + 1.
            #
            offset = _BOX_TOTAL_LINES if _HAS_TERMIOS else _BOX_TOTAL_LINES + 1
            _cursor_up(offset)

        _render_box(page, has_next)

        if has_next:
            if not _IS_TTY:
                pass                  # non-TTY: auto-advance, no blocking
            elif _HAS_TERMIOS:
                _read_enter_raw()     # silent — cursor stays on line below box
            else:
                input()               # echoes \\n — cursor moves one line down

    for text in passthrough_lines:
        print(text)
    print()


def print_hint(text: str) -> None:
    """Print a compact system/prompt line with no pacing."""
    if text:
        print(text)


def print_title_screen() -> None:
    """Render a centered title screen."""
    width = max(60, get_terminal_size(fallback=(80, 24)).columns)
    title_lines = [
        "████████╗██╗  ██╗███████╗    ██████╗  ██████╗  █████╗ ██████╗ ",
        "╚══██╔══╝██║  ██║██╔════╝    ██╔══██╗██╔═══██╗██╔══██╗██╔══██╗",
        "   ██║   ███████║█████╗      ██████╔╝██║   ██║███████║██║  ██║",
        "   ██║   ██╔══██║██╔══╝      ██╔══██╗██║   ██║██╔══██║██║  ██║",
        "   ██║   ██║  ██║███████╗    ██║  ██║╚██████╔╝██║  ██║██████╔╝",
        "   ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ",
        "                     Prologue: STILL HERE",
    ]
    print("\n" * 2)
    for line in title_lines:
        print(line.center(width))
    print()


def menu_choice(prompt: str, options: list[str]) -> int:
    """Simple numbered menu prompt; returns selected 0-based index."""
    print(prompt)
    for idx, option in enumerate(options, start=1):
        print(f"  [{idx}] {option}")
    while True:
        raw = input("\nSelect an option: ").strip()
        if raw.isdigit():
            picked = int(raw) - 1
            if 0 <= picked < len(options):
                return picked
        print(f"Please enter a number from 1 to {len(options)}.")


def print_hud(state, location_name: str) -> None:
    """Render a compact status bar before command input."""
    objective = state.current_objective if state.current_objective else "No objective"
    if len(objective) > 42:
        objective = objective[:39] + "..."
    top = "═" * 80
    info = (
        f"{state.player_name or 'Unknown'}  |  {location_name}  |  "
        f"{state.time_label}  |  Gold: {state.money}"
    )
    print()
    print(top)
    print(info)
    print(f"Objective: {objective}")
    print(top)


def print_status_screen(state, location_name: str) -> None:
    """Render a command-opened hub/status view."""
    print("\n" + "─" * 64)
    print("PLAYER STATUS")
    print("─" * 64)
    print(f"Name: {state.player_name or 'Unknown'}")
    print(f"Location: {location_name}")
    print(f"Time: {state.time_label}")
    print(f"Gold: {state.money}")
    print(f"Objective: {state.current_objective or 'No objective set'}")
    print()
    print("Inventory:")
    if state.inventory:
        for item in state.inventory:
            print(f"  - {item}")
    else:
        print("  - (empty)")
    print()
    print("Discovered locations:")
    if state.discovered_locations:
        print("  - " + ", ".join(state.discovered_locations))
    else:
        print("  - (none yet)")
    print("─" * 64)


def print_choices(prompt_lines: list[str], choices: list[str]) -> int:
    """
    Display a multiple-choice prompt and return the selected 0-based index.

    Unlike the paginated dialogue box, the choice box has no fixed height —
    it sizes to its content.  It does NOT participate in cursor-up redraws;
    it renders once and waits for numeric input.

    prompt_lines  Framing text shown above the numbered options.
                  May be empty if the situation is already clear.
    choices       List of option strings.  Each renders as "[N]  text".

    Returns the 0-based index of the selected choice.

    Example
    -------
    idx = print_choices(
        prompt_lines=["She looks at you. Waiting."],
        choices=[
            '"I\'m going. I have to find Nate."',
            '"I don\'t know yet."',
            "[Stay quiet]",
        ]
    )
    # idx is 0, 1, or 2
    """
    print()

    content_rows: list[str] = []

    # Wrap and collect prompt lines.
    for line in prompt_lines:
        content_rows.extend(_wrap_for_box(line))

    # One blank spacer between prompt and choices (only when there's a prompt).
    if content_rows:
        content_rows.append("")

    # Wrap and collect numbered choices.
    for i, choice in enumerate(choices, 1):
        content_rows.extend(_wrap_for_box(f"[{i}]  {choice}"))

    # Render the choice box (variable height — no _BOX_TOTAL_LINES constraint).
    top = "┌" + "─" * (_BOX_WIDTH - 2) + "┐"
    bot = "└" + "─" * (_BOX_WIDTH - 2) + "┘"

    _print_line(top)

    for row in content_rows:
        if _IS_TTY and row.strip():
            _typewrite_row(row)
        else:
            _print_line(f"│ {row:<{_CONTENT_WIDTH}} │")

    # Footer signals this is an input prompt, not a dialogue page.
    _print_line(f"│ {'  ◆ Choose':<{_CONTENT_WIDTH}} │")
    _print_line(bot)
    sys.stdout.flush()

    # Collect and validate numeric input below the box.
    while True:
        try:
            raw = input("  > ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return idx
            print(f"  (Enter a number from 1 to {len(choices)}.)")
        except ValueError:
            print(f"  (Enter a number from 1 to {len(choices)}.)")
