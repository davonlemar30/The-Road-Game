"""Town navigation engine for ISO Town node graph."""

from __future__ import annotations

from typing import Optional

from data.town_locations import TOWN_NODES


def _all_aliases() -> dict[str, str]:
    """Build a flat alias → node_id lookup across all town nodes."""
    lookup: dict[str, str] = {}
    for node_id, node in TOWN_NODES.items():
        lookup[node_id] = node_id
        lookup[node["name"].lower()] = node_id
        for alias in node["aliases"]:
            lookup[alias.lower()] = node_id
    return lookup


_ALIAS_MAP = _all_aliases()


class TownWorld:
    def __init__(self) -> None:
        self.nodes = TOWN_NODES

    def resolve(self, name: str) -> Optional[str]:
        """Return node_id for a name/alias string, or None if unrecognized."""
        return _ALIAS_MAP.get(name.strip().lower())

    def get_node(self, node_id: str) -> dict:
        return self.nodes[node_id]

    def describe(self, node_id: str) -> str:
        node = self.get_node(node_id)
        neighbor_names = [self.nodes[n]["name"] for n in node["neighbors"]]
        neighbors_str = ", ".join(neighbor_names)
        return f"\n[{node['name']}]\n{node['description']}\nNearby: {neighbors_str}"

    def move_to(self, current_id: str, target_name: str) -> tuple[bool, str]:
        """
        Attempt to move from current_id to a node matching target_name.
        Returns (success, result_node_id_or_error_message).
        Only allows movement to direct neighbors.
        """
        target_id = self.resolve(target_name)
        if target_id is None:
            return False, f"You don't know of a place called '{target_name}' from here."

        node = self.get_node(current_id)
        if target_id not in node["neighbors"]:
            dest_name = self.nodes[target_id]["name"]
            # Build hint from actual neighbors
            neighbor_names = [self.nodes[n]["name"] for n in node["neighbors"]]
            hint = "  •  ".join(neighbor_names)
            return False, (
                f"You can't get to {dest_name} directly from here.\n"
                f"(From here you can reach: {hint})"
            )

        return True, target_id

    def neighbors_text(self, node_id: str) -> str:
        node = self.get_node(node_id)
        names = [self.nodes[n]["name"] for n in node["neighbors"]]
        return ", ".join(names)

    def inspect(self, node_id: str, target: str) -> str:
        node = self.get_node(node_id)
        key = target.strip().lower()
        details = node.get("interactables", {})
        if key in details:
            return details[key]
        # Partial match
        for k, v in details.items():
            if key in k:
                return v
        return "You don't notice anything like that here."
