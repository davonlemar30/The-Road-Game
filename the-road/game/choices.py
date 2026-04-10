"""Reusable hidden-choice runner and effect utilities."""

from __future__ import annotations

from data.choices_data import SCENE_CHOICES
from game.display import print_dialogue


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
    print_dialogue([choice["prompt"]])
    for idx, option in enumerate(options, start=1):
        print(f"  {idx}. {option['text']}")

    selected = None
    while selected is None:
        raw = input("\nChoose an option number: ").strip()
        if not raw.isdigit():
            print("Please enter the number of your choice.")
            continue
        index = int(raw)
        if index < 1 or index > len(options):
            print(f"Enter a number between 1 and {len(options)}.")
            continue
        selected = options[index - 1]

    apply_choice_effects(state, selected.get("effects", {}))
    state.choice_history.add(choice_id)

    response_lines = selected.get("response_lines", [])
    if response_lines:
        print_dialogue(response_lines)

    return selected.get("id")
