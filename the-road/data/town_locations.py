"""ISO Town node definitions for The Road — Scene One exit through Scene Two entry.

Nine canonical locations. Each node has:
  id          — used internally as the state key
  name        — display name
  aliases     — set of strings that `go <alias>` will accept
  description — shown on 'look' (player-triggered only)
  neighbors   — list of node ids directly reachable from here
  interactables — dict of inspect targets
"""

TOWN_NODES: dict[str, dict] = {

    # ── FRONT STREET ─────────────────────────────────────────────────────────
    # Immediate outside of GP's House — first breath of town.
    "front_street": {
        "name": "Front Street",
        "aliases": {"front street", "front", "street", "home", "outside", "out"},
        "description": (
            "The air out here is cooler than the house. The street is quiet this early, "
            "but not empty — a few people moving with the particular purpose of people "
            "who've already decided on their day. GP's House is behind you. "
            "Iso Town spreads out ahead."
        ),
        "neighbors": ["the_square"],
        "interactables": {
            "house": "The door is closed behind you now. You don't need to go back.",
            "street": "Worn smooth. A lot of people have passed through here. A lot more will.",
            "neighbors": "A few houses close together. Quiet. People keeping their own hours.",
        },
    },

    # ── THE SQUARE ────────────────────────────────────────────────────────────
    # Central hub of Iso Town. Most paths branch from here.
    "the_square": {
        "name": "The Square",
        "aliases": {
            "the square", "square", "town square", "center", "town center", "main square",
        },
        "description": (
            "The center of Iso Town is open and deliberate — wide enough that the sky feels "
            "present. A few vendors are setting up early. The announcement board near the "
            "water station has new notices, but you're not close enough to read them. "
            "Paths splay out in every direction from here."
        ),
        "neighbors": ["front_street", "the_market", "the_commons", "foundation_steps"],
        "interactables": {
            "board": (
                "Community notices. Shift rotations. A hand-drawn map of the outer fence. "
                "One sheet in the corner reads: 'Attunement intake — contact The Keeper.'"
            ),
            "water station": "A communal cistern. Clean and managed. People stop here on their way somewhere.",
            "vendors": "Early risers getting their stalls ready. Fruit, tools, hand-sewn things. Practical goods.",
        },
    },

    # ── THE MARKET ────────────────────────────────────────────────────────────
    "the_market": {
        "name": "The Market",
        "aliases": {"the market", "market", "market row", "stalls", "shops"},
        "description": (
            "A covered row of stalls that smells like earth and warm bread and something "
            "medicinal you can't place. People barter more than they spend — tokens exist "
            "but trust moves faster. You don't need anything yet. But it's useful to know "
            "where things are."
        ),
        "neighbors": ["the_square", "the_archive"],
        "interactables": {
            "stalls": "Practical goods mostly. Food, repair supplies, preserved items. Nothing flashy.",
            "herbalist": (
                "A stall in the corner with jars of things you half-recognize. "
                "The person behind it clocks you, nods once, goes back to sorting leaves."
            ),
            "tokens": "Small pressed discs with a crest stamped on them. The local exchange medium. You don't have any.",
        },
    },

    # ── THE COMMONS ───────────────────────────────────────────────────────────
    "the_commons": {
        "name": "The Commons",
        "aliases": {"the commons", "commons", "community space", "gathering", "park"},
        "description": (
            "A wide clearing kept deliberately open. Benches along the edges, a firepit "
            "in the center that's cold at this hour. This is where Iso Town does its "
            "thinking — town meetings, disputes, quiet mornings like this one. "
            "Not empty. Just settled."
        ),
        "neighbors": ["the_square", "fence_line", "foundation_steps"],
        "interactables": {
            "firepit": "Cold ash and old wood. Not abandoned — just resting between uses.",
            "benches": (
                "Worn smooth and well-used. Someone carved a small crest into the end of one. "
                "Not vandalism. A marker."
            ),
            "notice tree": (
                "A tree with bark worn by pinned notices over many years. "
                "The current ones are about fence patrol assignments and a missing supply crate."
            ),
        },
    },

    # ── FOUNDATION STEPS ─────────────────────────────────────────────────────
    # Where Caldren Vale runs Crest trials.
    "foundation_steps": {
        "name": "Foundation Steps",
        "aliases": {
            "foundation steps", "foundation", "steps", "caldren", "crest trial", "trial",
        },
        "description": (
            "Wide stone steps descending into a sunken courtyard. Functional, not ornamental. "
            "The walls are etched with Crest symbols from every trial that's been completed here. "
            "A man in a weathered coat stands near the far wall, not doing anything in particular. "
            "He looks like someone who is always watching even when he isn't."
        ),
        "neighbors": ["the_square", "the_commons"],
        "interactables": {
            "crest symbols": (
                "Dozens carved into the stone, some old enough that the edges have softened. "
                "No two are exactly the same — earned, not stamped."
            ),
            "caldren": (
                "He turns to look at you. 'Not today,' he says, before you've said anything. "
                "'But soon.' He goes back to watching the courtyard."
            ),
            "courtyard": "Open, measured, uncluttered. Designed so nothing is hidden and no one can hide.",
        },
    },

    # ── THE ARCHIVE ───────────────────────────────────────────────────────────
    "the_archive": {
        "name": "The Archive",
        "aliases": {"the archive", "archive", "library", "records", "study"},
        "description": (
            "Low ceilings and natural light through narrow windows. Shelves of preserved "
            "materials — printed pages, bound notebooks, salvaged documents. "
            "Someone has organized them obsessively. Another person has clearly been "
            "going through a section near the back and hasn't put things away properly. "
            "Recent, by the look of it."
        ),
        "neighbors": ["the_market", "keepers_dome"],
        "interactables": {
            "shelves": "Organized by region, then era. Dense and comprehensive for a town this size.",
            "disturbed section": (
                "A cluster of field notebooks pulled from their spots, a few left open. "
                "The pages are about the outer trails — Mystic, Forbidden. "
                "Recent handwriting in the margins. Not the archivist's."
            ),
            "archivist": (
                "Older. Absorbed. Looks up at you without moving their head. "
                "'If you're looking for field notes on the outer trails, someone beat you to it.' "
                "Back to their work."
            ),
        },
    },

    # ── THE KEEPER'S DOME ─────────────────────────────────────────────────────
    # Bob's lab. Scene 2 entry point.
    "keepers_dome": {
        "name": "The Keeper's Dome",
        "aliases": {
            "keepers dome", "keeper's dome", "the dome", "dome", "bob", "bob's lab",
            "keeper", "lab", "bob lab",
        },
        "description": (
            "Low, round, and set back from the path where foot traffic naturally thins. "
            "The outer wall is thick and the door is barely ajar. Something alive moves "
            "inside — you can feel it more than hear it. The smell is old paper and "
            "something warm that you can't name. "
            "A ring of symbols is cut into the stone threshold."
        ),
        "neighbors": ["the_archive", "fence_line", "mystic_trail"],
        "interactables": {
            "threshold": (
                "The ring of symbols pressed into the stone. "
                "Attunement marks — you recognize the shape from something Mom mentioned once."
            ),
            "door": (
                "Barely open. The gap is deliberate. "
                "Inside you can see the edge of a workbench covered in materials you don't recognize."
            ),
            "attunement ring": (
                "Cut directly into the floor just inside the threshold. "
                "Old. Used. The stone around it is worn smooth from years of people standing there."
            ),
        },
    },

    # ── FENCE LINE ────────────────────────────────────────────────────────────
    # Town boundary. The edge of the known.
    "fence_line": {
        "name": "The Fence Line",
        "aliases": {
            "fence line", "fence", "the fence", "town edge", "edge", "boundary",
        },
        "description": (
            "The outer boundary of Iso Town. The fence itself is solid — repaired many times "
            "over many years, you can tell by the seams. Beyond it the ground changes: "
            "less managed, less lit, more honest about what it is. "
            "A patrol walks the perimeter on a schedule. You're between rounds."
        ),
        "neighbors": ["the_commons", "keepers_dome"],
        "interactables": {
            "fence": (
                "Reinforced and layered. Not a wall — deliberate. "
                "Iso Town isn't trying to keep people in. It's trying to keep something else out."
            ),
            "gate": (
                "Bolted from this side. There's a log of who passes through. "
                "Names, times, direction. No Astari on record yet for yours."
            ),
            "patrol path": "Worn dirt in a loop along the inside of the fence. Regular footsteps. Reliable.",
        },
    },

    # ── MYSTIC TRAIL ENTRANCE ─────────────────────────────────────────────────
    # Where the trail begins. Connects Iso Town to the wider world.
    "mystic_trail": {
        "name": "Mystic Trail",
        "aliases": {
            "mystic trail", "mystic", "trail", "trail entrance", "trailhead", "the trail",
        },
        "description": (
            "The trail mouth opens up behind the Dome, half-sheltered by overgrowth. "
            "The path is clear for the first stretch — you can see maybe fifty yards before "
            "it bends and the canopy thickens. The Forbidden Trail branches somewhere deeper in. "
            "You can feel the difference between here and there before you've gone anywhere."
        ),
        "neighbors": ["keepers_dome"],
        "interactables": {
            "path": (
                "Worn and readable for now. Nate's been on this trail — "
                "you can see signs if you know what to look for. Recent passage."
            ),
            "overgrowth": (
                "Dense at the edges. The kind that takes years to get this thick. "
                "Something about it feels intentional."
            ),
            "trail marker": (
                "An old post with symbols burned into it. "
                "Mystic Trail on one face. The other face has been deliberately scratched out."
            ),
        },
    },
}
