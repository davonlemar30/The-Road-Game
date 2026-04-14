"""
Dialogue Mode framework for The Road.

Drives structured NPC conversations as a series of beats, each consisting
of optional narrative/dialogue lines followed by an optional player choice.

Usage
─────
    session = DialogueSession(
        npc_name="Your Mom",
        beats=[
            Beat(lines=MOTHER_SCENE1_PART1, choice_id="mom_sleep_response"),
            Beat(lines=MOTHER_SCENE1_PART2, choice_id="mom_nate_response"),
        ],
        closing_hint="She's here if there's more on your mind.",
    )
    session.run(state, renderer)

Visual output
─────────────
    ─── Your Mom ─────────────────────────────────────────────────────────────────
    [dialogue box]
    [choice box]
    [dialogue box]
    [choice box]
    She's here if there's more on your mind.
    ──────────────────────────────────────────────────────────────────────────────

The header and footer create a clear Dialogue Mode boundary, visually distinct
from general parser output.  Everything inside is NPC-space.

The parser (ask mom, ask bob) still works at any time and is NOT wrapped in
a session — it remains secondary/optional.  DialogueSession handles the
primary curated story beats only.
"""

from __future__ import annotations

from game.choices import run_scene_choice
from game.display import print_dialogue, print_hint
from game.ui.view_models import SceneView

_LINE_WIDTH: int = 80


def _npc_header(npc_name: str) -> None:
    """Print the opening rule line with the NPC name embedded."""
    prefix = f"─── {npc_name} "
    remaining = max(0, _LINE_WIDTH - len(prefix))
    print(f"\n{prefix}{'─' * remaining}")


def _npc_footer() -> None:
    """Print the closing rule line."""
    print("─" * _LINE_WIDTH)


# ── Core data types ───────────────────────────────────────────────────────────

class Beat:
    """
    One unit of a dialogue session.

    lines       NPC/narrative lines passed to print_dialogue().  May be empty
                if this beat is purely a choice prompt.

    choice_id   Optional key into SCENE_CHOICES.  When set, run_scene_choice()
                is called after the lines are displayed.  Idempotency is
                handled by run_scene_choice itself (won't re-fire if already
                in choice_history).
    """

    def __init__(
        self,
        lines: list[str] | None = None,
        choice_id: str | None = None,
    ) -> None:
        self.lines: list[str] = lines or []
        self.choice_id: str | None = choice_id


# ── Session runner ────────────────────────────────────────────────────────────

class DialogueSession:
    """
    Runs a structured NPC conversation as an ordered sequence of beats.

    Parameters
    ──────────
    npc_name        Shown in the header rule (e.g. "Your Mom", "Keeper Bob").
    beats           Ordered list of Beat objects.
    closing_hint    Optional plain-text hint printed below the last beat,
                    before the footer rule.  Use for parser nudges
                    (e.g. "She's here if there's more on your mind.").
    """

    def __init__(
        self,
        npc_name: str,
        beats: list[Beat],
        closing_hint: str = "",
    ) -> None:
        self.npc_name = npc_name
        self.beats = beats
        self.closing_hint = closing_hint

    def run(self, state, renderer=None) -> dict[str, str]:
        """
        Execute the full session.

        Prints the header, iterates over beats, prints the optional closing
        hint, then prints the footer.

        Returns a dict of {choice_id: selected_option_id} for every choice
        that was resolved during this session.  Beats whose choice_id was
        already in state.choice_history produce no entry in the dict
        (run_scene_choice returns None and we skip them).
        """
        if renderer is not None:
            renderer.show_dialogue_header(self.npc_name)
        else:
            _npc_header(self.npc_name)

        results: dict[str, str] = {}

        for beat in self.beats:
            if beat.lines:
                if renderer is not None:
                    renderer.render(
                        SceneView(
                            current_mode="dialogue",
                            speaker_name=self.npc_name,
                            dialogue_lines=beat.lines,
                        )
                    )
                else:
                    print_dialogue(beat.lines)
            if beat.choice_id:
                selected = run_scene_choice(state, beat.choice_id, renderer=renderer)
                if selected is not None:
                    results[beat.choice_id] = selected

        if self.closing_hint:
            if renderer is not None:
                renderer.render(
                    SceneView(
                        current_mode="dialogue",
                        speaker_name=self.npc_name,
                        footer_hint=self.closing_hint,
                    )
                )
            else:
                print_hint(self.closing_hint)

        if renderer is not None:
            renderer.show_dialogue_footer()
        else:
            _npc_footer()
        return results
