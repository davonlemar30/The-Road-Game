"""
Terminal display utilities for The Road.

Separates NPC dialogue from system text with a framed, paginated dialogue box.

Design decisions:
  - Dialogue is shown in a fixed-width frame (Phase 2).
  - Content is paginated into small chunks and advances on Enter (Phase 1).
  - In non-interactive mode (stdin not a TTY), dialogue auto-advances so
    scripted tests do not hang.
  - System/hint lines still print outside the frame.
"""

from __future__ import annotations

import sys
import textwrap

_BOX_WIDTH: int = 78
_CONTENT_WIDTH: int = _BOX_WIDTH - 4
_PAGE_LINES: int = 3
_CONTINUE_PROMPT: str = "  ▶ Press Enter to continue..."


def _wrap_for_box(line: str) -> list[str]:
    """Wrap one script line into visual box rows."""
    if not line.strip():
        return [""]
    return textwrap.wrap(
        line.strip(),
        width=_CONTENT_WIDTH,
        replace_whitespace=True,
        drop_whitespace=True,
    )


def _paginate(rows: list[str], page_size: int = _PAGE_LINES) -> list[list[str]]:
    """Split visual rows into page chunks."""
    if not rows:
        return [[]]
    return [rows[i:i + page_size] for i in range(0, len(rows), page_size)]


def _render_box(rows: list[str], has_next: bool) -> None:
    """Render one dialogue page inside an ASCII frame."""
    print("\n".join(_box_lines(rows, has_next)))


def _box_lines(rows: list[str], has_next: bool) -> list[str]:
    """Build one framed page as plain text lines."""
    lines = ["┌" + "─" * (_BOX_WIDTH - 2) + "┐"]
    for row in rows:
        lines.append(f"│ {row:<{_CONTENT_WIDTH}} │")

    # Keep a stable box height so the screen doesn't jump.
    for _ in range(max(0, _PAGE_LINES - len(rows))):
        lines.append(f"│ {'':<{_CONTENT_WIDTH}} │")

    marker = "▼" if has_next else "■"
    footer = f"{marker} Enter"
    lines.append(f"│ {footer:<{_CONTENT_WIDTH}} │")
    lines.append("└" + "─" * (_BOX_WIDTH - 2) + "┘")
    return lines


def _wait_for_continue(has_next: bool) -> None:
    """Pause until player confirms continuation (TTY only)."""
    if not has_next:
        return
    if not sys.stdin.isatty():
        return
    input(_CONTINUE_PROMPT)


def print_dialogue(lines: list) -> None:
    """
    Print a block of NPC lines in a paginated dialogue frame.

    Hint/meta lines (starting with "(" or "\n") are printed after the
    dialogue box, unchanged.
    """
    print()
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
    interactive = sys.stdin.isatty()
    rendered_lines = 0
    for idx, page in enumerate(pages):
        has_next = idx < len(pages) - 1
        if interactive and rendered_lines:
            # Keep a stationary text box: move cursor up and redraw in place.
            print(f"\x1b[{rendered_lines}A", end="")
        box = _box_lines(page, has_next)
        rendered_lines = len(box)
        print("\n".join(box))
        _wait_for_continue(has_next)

    for text in passthrough_lines:
        print(text)
    print()


def print_hint(text: str) -> None:
    """Print a compact system / prompt line with no pacing."""
    if text:
        print(text)
