"""
Renderer — the single choke point between game logic and terminal output.

Status (Task 2 — active):
    GameEngine now uses this class for all engine-level I/O.
    display.py is the rendering backend; its internals are untouched.
    DialogueSession and choices.py still call display.py directly (intentional —
    they are self-contained; wrapping them is a Task 3 concern).

Why not Textual (for now):
    display.py already implements stationary-frame TTY redraws, termios raw
    input, typewriter animation, and multi-environment fallbacks (CI / piped).
    Migrating to Textual's event loop would replace all of that at high risk.
    The cleaner path when fixed-screen layout is needed:
      1. Engine → Renderer → SceneView (view_models.py) — this file is step 1.
      2. Renderer draws a stable HUD region + scrollable system-text region
         using ANSI cursor positioning built on top of display.py primitives.
      3. Only if that proves insufficient: evaluate a minimal Rich Live layout.

Coupling map (Task 2 complete):
    engine print(text)                 → renderer.show_system(text)   ✓
    engine print(line) × N             → renderer.show_lines(lines)   ✓
    engine input(prompt)               → renderer.get_input(prompt)   ✓
    engine input(free-text prompt)     → renderer.get_text_input(p)   ✓
    display.print_hud(state, loc)      → renderer.show_hud(...)       ✓
    display.print_dialogue(lines)      → renderer.show_dialogue(...)  ✓
    display.print_hint(text)           → renderer.show_hint(...)      ✓
    display.print_choices(p, c)        → renderer.show_choices(...)   ✓  (via choices.py)
    display.print_status_screen(s, l)  → renderer.show_status(...)    ✓
    display.print_title_screen()       → renderer.show_title()        ✓
    display.menu_choice(prompt, opts)  → renderer.show_menu(...)      ✓

    dialogue_session._npc_header/footer stay internal to DialogueSession.
    choices.run_scene_choice calls display.py directly — unchanged for now.
"""

from __future__ import annotations

from game.display import (
    menu_choice as _menu_choice,
    print_choices as _print_choices,
    print_dialogue as _print_dialogue,
    print_hint as _print_hint,
    print_hud as _print_hud,
    print_status_screen as _print_status_screen,
    print_title_screen as _print_title_screen,
)


class Renderer:
    """
    Wraps all terminal output for The Road.

    GameEngine holds one instance (self.renderer) and calls these methods
    instead of calling print(), input(), or display.py functions directly.

    Every method currently delegates to the existing display.py helpers,
    which preserves all existing TTY detection and animation logic.
    Nothing in display.py was changed.
    """

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

    # ── HUD ───────────────────────────────────────────────────────────────────

    def show_hud(self, state, location_name: str) -> None:
        """
        Render the persistent header bar above the command prompt.

        Task 3 target: keep the HUD anchored at a fixed screen position
        rather than reprinting it each loop iteration.
        """
        _print_hud(state, location_name)

    # ── Dialogue mode ─────────────────────────────────────────────────────────

    def show_dialogue(self, lines: list[str]) -> None:
        """
        Paginated NPC dialogue box with typewriter animation.

        Used by engine for the small number of direct print_dialogue() calls
        that exist outside DialogueSession (ask fallback, scene2 hook).
        DialogueSession still calls display.py directly for now.
        """
        _print_dialogue(lines)

    def show_hint(self, text: str) -> None:
        """Single-line meta hint printed outside the dialogue frame."""
        _print_hint(text)

    def show_choices(self, prompt_lines: list[str], choices: list[str]) -> int:
        """
        Framed numeric choice box; returns selected 0-based index.
        choices.run_scene_choice calls display.print_choices directly — unchanged.
        """
        return _print_choices(prompt_lines, choices)

    # ── System / explore mode ─────────────────────────────────────────────────

    def show_system(self, text: str) -> None:
        """
        Emit one transient engine feedback line or block.

        Covers: navigation results, error messages, objective updates, save
        confirmations, transition prose, and any other single print() call
        that was previously scattered across engine handler methods.

        In a fixed-screen renderer this will route text into a bounded scroll
        region instead of flowing it past the HUD.
        """
        print(text)

    def show_lines(self, lines: list[str]) -> None:
        """
        Emit a sequence of engine feedback lines, preserving order.

        Use instead of show_system() when the output is built as a list
        (e.g. inventory, help, cinematic transition blocks).  Each element
        is printed as its own line.

        In a fixed-screen renderer this feeds the same scroll region as
        show_system(), but arrives pre-batched for cleaner buffering.
        """
        for line in lines:
            print(line)

    # ── Input ─────────────────────────────────────────────────────────────────

    def get_input(self, prompt: str = "\n> ") -> str:
        """
        Block for the main command prompt input.

        Wraps input().  In a fixed-screen renderer this will position the
        cursor inside a dedicated input region at the bottom of the screen.
        """
        return input(prompt)

    def get_text_input(self, prompt: str) -> str:
        """
        Block for free-text input (e.g. name entry at game start).

        Separate from get_input() so a future renderer can style or position
        these prompts differently from the command-line cursor.
        """
        return input(prompt)
