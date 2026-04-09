"""
Terminal display utilities for The Road.

Separates NPC dialogue from system text both visually and in pacing.

Design decisions:
  - Speech lines (contain quotes) get a short pause before printing so
    the eye has time to settle between lines.  No per-character output —
    that gets annoying fast in a real session.
  - Stage-direction / narration lines get a shorter pause.
  - System/hint text is printed instantly via print_hint(); no indentation.
  - A blank line is added before and after every dialogue block so it
    never runs flush against the prompt or system messages.
"""

import time

_SPEECH_PAUSE: float = 0.13    # seconds before each quoted speech line
_NARRATION_PAUSE: float = 0.05  # seconds before each narration line


def _is_speech(line: str) -> bool:
    """True for lines that contain quotation marks (NPC actual speech)."""
    return '"' in line


def print_dialogue(lines: list) -> None:
    """
    Print a block of NPC lines with visual indentation and pacing.

    Quoted speech lines are indented two spaces and preceded by a short
    pause.  Narration / stage-direction lines get the same indent but a
    briefer pause.  Blank or hint-style lines (starting with '(' or a
    newline) are passed through without indentation or delay.
    """
    print()  # leading breath before dialogue
    for line in lines:
        stripped = line.strip()

        if not stripped:
            # Preserve intentional blank lines in a sequence
            print()
            continue

        if stripped.startswith("(") or stripped.startswith("\n"):
            # Hint / meta text — no pacing, no indent
            print(line)
            continue

        if _is_speech(line):
            time.sleep(_SPEECH_PAUSE)
            print(f"  {line}")
        else:
            time.sleep(_NARRATION_PAUSE)
            print(f"  {line}")

    print()  # trailing breath after dialogue


def print_hint(text: str) -> None:
    """Print a compact system / prompt line with no pacing."""
    if text:
        print(text)
