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

    Returns selected option id, or None if choice_id is unknown.
    """
    choice = SCENE_CHOICES.get(choice_id)
    if not choice:
        return None

    options = choice["options"]
    selected_index = print_choices(
        prompt_lines=[choice["prompt"]],
        choices=[opt["text"] for opt in options],
    )
    selected = options[selected_index]

    apply_choice_effects(state, selected.get("effects", {}))
    state.choice_history.add(choice_id)

    response_lines = selected.get("response_lines", [])
    if response_lines:
        print_dialogue(response_lines)

    return selected.get("id")
