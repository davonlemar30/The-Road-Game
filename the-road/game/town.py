"""Town navigation engine for ISO Town node graph."""

from __future__ import annotations

import re
from typing import Optional

from data.town_locations import TOWN_NODES


def _normalize_place(text: str) -> str:
    text = text.lower().strip().replace("’", "'")
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [w for w in text.split() if w not in {"to", "the", "at"}]
    return " ".join(words)


def _all_aliases() -> dict[str, str]:
    """Build a flat alias → node_id lookup across all town nodes."""
    lookup: dict[str, str] = {}
    for node_id, node in TOWN_NODES.items():
        lookup[_normalize_place(node_id)] = node_id
        lookup[_normalize_place(node["name"])] = node_id
        for alias in node["aliases"]:
            lookup[_normalize_place(alias)] = node_id
    return lookup


_ALIAS_MAP = _all_aliases()


class TownWorld:
    def __init__(self) -> None:
        self.nodes = TOWN_NODES

    def resolve(self, name: str) -> Optional[str]:
        """Return node_id for a name/alias string, or None if unrecognized."""
        normalized = _normalize_place(name)
        return _ALIAS_MAP.get(normalized)

    def get_node(self, node_id: str) -> dict:
        return self.nodes[node_id]

    def describe(self, node_id: str) -> str:
        node = self.get_node(node_id)
        neighbor_names = [self.nodes[n]["name"] for n in node["neighbors"]]
        neighbors_str = ", ".join(neighbor_names)
        lines = [f"\n[{node['name']}]", node["description"]]
        visible_npcs = node.get("visible_npcs", [])
        if visible_npcs:
            lines.append(f"Visible people: {', '.join(visible_npcs)}")
        pois = node.get("points_of_interest", [])
        if pois:
            lines.append(f"Points of interest: {', '.join(pois)}")
        if node.get("shops"):
            lines.append("Shops nearby: " + ", ".join(shop["name"] for shop in node["shops"]))
        lines.append(f"From here you can head toward: {neighbors_str}")
        return "\n".join(lines)

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

    def browse(self, node_id: str, target: str = "") -> tuple[bool, str]:
        node = self.get_node(node_id)
        shops = node.get("shops", [])
        if not shops:
            return False, "There's nothing to browse here."

        if target:
            key = target.strip().lower()
            for shop in shops:
                aliases = {shop["name"].lower(), *(a.lower() for a in shop.get("aliases", []))}
                if key in aliases:
                    items = "\n".join(f"  - {i['name']} ({i['price']} gold)" for i in shop.get("items", []))
                    return True, f"\n[{shop['name']}]\n{shop['description']}\n{items}"

        summaries = [f"- {shop['name']}: {shop['description']}" for shop in shops]
        return True, "You scan the nearby stalls:\n" + "\n".join(summaries)

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
