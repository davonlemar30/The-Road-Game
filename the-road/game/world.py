"""World helpers for locations and movement."""

from data.locations import LOCATIONS


class World:
    def __init__(self) -> None:
        self.locations = LOCATIONS

    def get_location(self, location_id: str) -> dict:
        return self.locations[location_id]

    def describe_location(self, location_id: str) -> str:
        location = self.get_location(location_id)
        exits = ", ".join(location["exits"].keys())
        return f"\n[{location['name']}]\n{location['description']}\nExits: {exits}"

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
