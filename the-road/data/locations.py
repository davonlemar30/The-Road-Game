"""Static location content for Phase 1 of The Road."""

LOCATIONS = {
    "bedroom": {
        "name": "Bedroom",
        "description": (
            "Your room is quiet except for the old ceiling fan. Books and notes are stacked "
            "in unfinished towers. You have stayed in this same loop for too long."
        ),
        "exits": {
            "south": "living_room",
        },
        "interactables": {
            "bookshelf": (
                "A crowded shelf of things you meant to learn. Every spine feels like a "
                "promise you postponed."
            ),
            "mirror": (
                "The reflection is familiar and almost invisible, like someone blending "
                "into the furniture."
            ),
            "window": (
                "Outside looks distant and unchanged. The world feels reachable, but not "
                "for free."
            ),
        },
    },
    "living_room": {
        "name": "Living Room",
        "description": (
            "The living room smells like old tea and quiet routines. The TV glows in the "
            "corner, filling the silence."
        ),
        "exits": {
            "north": "bedroom",
            "east": "kitchen",
            "south": "front_door",
        },
        "interactables": {
            "tv": (
                "Old pre-collapse programming loops endlessly across the screen. Nobody "
                "knows why the signal still comes through."
            ),
        },
    },
    "kitchen": {
        "name": "Kitchen",
        "description": (
            "A small kitchen with chipped cabinets, a clean sink, and a kettle waiting "
            "for water. Everything is practical, worn, and cared for."
        ),
        "exits": {
            "west": "living_room",
        },
        "interactables": {
            "kettle": "Cold metal. You can almost hear mornings that started better.",
        },
    },
    "front_door": {
        "name": "Front Door",
        "description": (
            "The front door is reinforced and heavy. The street beyond it is quiet in "
            "the way danger can be quiet."
        ),
        "exits": {
            "north": "living_room",
            "out": "outside",
        },
        "interactables": {
            "door": "The lock clicks softly when you test it.",
        },
    },
}
