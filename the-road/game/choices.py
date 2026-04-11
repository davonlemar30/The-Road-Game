"""Reusable hidden-choice runner and effect utilities."""

from __future__ import annotations

from data.choices_data import SCENE_CHOICES
from game.display import print_choices, print_dialogue


def apply_choice_effects(state, effects: dict) -> None:
    """Apply hidden narrative effects to runtime state."""
    state.reputation += effects.get("reputation", 0)
    state.disposition += effects.get("disposition", 0)

    for rel_key, delta in effects.get("relationships", {}).items():
        state.relationships[rel_key] = state.relationships.get(rel_key, 0) + delta

    for marker in effects.get("history", []):
        state.choice_history.add(marker)


def run_scene_choice(state, choice_id: str) -> str | None:
    """
    Render a formal choice prompt, gather numeric input, apply hidden effects,
    and show optional follow-up lines.

    Returns selected option id, or None if choice_id is unknown or already used.

    Idempotent: a second call with the same choice_id is a no-op.  This means
    engine call sites don't need to guard against double-triggers themselves.
    """
    choice = SCENE_CHOICES.get(choice_id)
    if not choice:
        return None

    # Guard: don't re-present a choice the player has already made this session.
    if choice_id in state.choice_history:
        return None

    options = choice["options"]
    prompt_lines = choice.get("prompt_lines") or [choice.get("prompt", "")]
    option_texts = [opt["text"] for opt in options]

    # Unified display: prompt + numbered choices in one framed box.
    idx = print_choices(prompt_lines, option_texts)
    selected = options[idx]

    apply_choice_effects(state, selected.get("effects", {}))
    state.choice_history.add(choice_id)

    response_lines = selected.get("response_lines", [])
    if response_lines:
        print_dialogue(response_lines)

    return selected.get("id")
