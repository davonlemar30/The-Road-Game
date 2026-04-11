"""World helpers for locations and movement."""

from __future__ import annotations

from data.locations import LOCATIONS

# Cardinal directions are still valid movement aliases, but we prefer not to
# surface them in the player-facing "Exits:" line when room-based names exist.
_CARDINAL_ALIASES: frozenset[str] = frozenset(
    {"north", "south", "east", "west", "up", "down", "in", "back", "leave", "inside"}
)


class World:
    def __init__(self) -> None:
        self.locations = LOCATIONS

    def get_location(self, location_id: str) -> dict:
        return self.locations[location_id]

    def describe_location(self, location_id: str) -> str:
        location = self.get_location(location_id)
        exits = self._display_exits(location["exits"])
        return f"\n[{location['name']}]\n{location['description']}\n\nExits: {exits}"

    def _display_exits(self, exits: dict) -> str:
        """Return a clean, player-facing list of exit names.

        Prefers room-based names over raw cardinal directions.
        Only falls back to cardinals if nothing else is available.
        """
        preferred = [k for k in exits if k not in _CARDINAL_ALIASES]
        if preferred:
            return ", ".join(preferred)
        # Fallback: nothing non-cardinal exists (shouldn't happen in practice).
        return ", ".join(exits.keys())

    def move(self, from_location: str, direction: str) -> tuple[bool, str]:
        location = self.get_location(from_location)
        destination = location["exits"].get(direction)
        if destination is None:
            return False, "You can't go that way."
        return True, destination

    def inspect(self, location_id: str, target: str) -> str:
        target_key = target.strip().lower()
        location = self.get_location(location_id)
        details = location.get("interactables", {})
        if target_key in details:
            return details[target_key]
        return "You don't notice anything like that here."
