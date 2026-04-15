"""Save and load game state to/from a JSON file."""

from __future__ import annotations

import json
import os
from typing import Union

from game.state import GameState

SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")


def save_game(state: GameState) -> str:
    os.makedirs(SAVE_DIR, exist_ok=True)
    data = {
        "player_name": state.player_name,
        "current_location": state.current_location,
        "current_objective": state.current_objective,
        "money": state.money,
        "day": state.day,
        "minutes_since_midnight": state.minutes_since_midnight,
        "inventory": state.inventory,
        "side_objectives": state.side_objectives,
        "journal_notes": state.journal_notes,
        "questions_asked": state.questions_asked,
        "discovered_locations": state.discovered_locations,
        "reputation": state.reputation,
        "disposition": state.disposition,
        "relationships": state.relationships,
        "choice_history": sorted(state.choice_history),
        "flags": state.flags,
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return "Game saved."


def load_game() -> tuple[bool, Union[GameState, str]]:
    """
    Returns (True, GameState) on success, or (False, error_message) on failure.
    """
    if not os.path.exists(SAVE_FILE):
        return False, "No save file found."
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
        state = GameState()
        state.player_name = data.get("player_name", "")
        state.current_location = data.get("current_location", "bedroom")
        state.current_objective = data.get("current_objective", "")
        state.money = data.get("money", 12)
        state.day = data.get("day", 1)
        state.minutes_since_midnight = data.get("minutes_since_midnight", 8 * 60)
        state.inventory = data.get("inventory", [])
        state.side_objectives = data.get("side_objectives", [])
        state.journal_notes = data.get("journal_notes", [])
        state.questions_asked = data.get("questions_asked", [])
        state.discovered_locations = data.get("discovered_locations", [])
        state.reputation = data.get("reputation", 0)
        state.disposition = data.get("disposition", 0)
        saved_relationships = data.get("relationships", {})
        state.relationships.update(saved_relationships)
        state.choice_history = set(data.get("choice_history", []))
        # Merge saved flags into defaults so new flags don't break old saves
        saved_flags = data.get("flags", {})
        state.flags.update(saved_flags)
        return True, state
    except (json.JSONDecodeError, KeyError) as e:
        return False, f"Save file corrupted: {e}"
