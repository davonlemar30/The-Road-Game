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
            "The air out here is cooler than the house. The street is quiet this early — "
            "not empty, but moving at the pace of people who've already settled into their morning. "
            "Something about it feels held. The kind of calm that knows itself. "
            "GP's House is behind you. Iso Town spreads out ahead."
        ),
        "neighbors": ["the_square"],
        "interactables": {
            "house": "The door is closed behind you now. You don't need to go back.",
            "street": "Worn smooth. A lot of people have passed through here. A lot more will.",
            "neighbors": "A few houses close together. Quiet. People keeping their own hours.",
        },
        "visible_npcs": [],
        "points_of_interest": ["Home gate", "Weathered way-sign toward The Square"],
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
        "visible_npcs": ["Old Guard"],
        "points_of_interest": ["Announcement board", "Water station", "Directional sign toward Keeper's Dome"],
    },

    # ── THE MARKET ────────────────────────────────────────────────────────────
    "the_market": {
        "name": "The Market",
        "aliases": {"the market", "market", "market row", "stalls", "shops"},
        "description": (
            "A covered row of stalls that smells like earth and warm bread and something "
            "medicinal you can't place. People barter more than they spend — gold exists "
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
            "tokens": "Small pressed discs with a crest stamped on them. Local gold markers for everyday exchange. You don't have much yet.",
        },
        "visible_npcs": ["Fruit Vendor"],
        "points_of_interest": ["Striped awning stall", "Herbalist corner", "Gold board"],
        "shops": [
            {
                "name": "Striped Awning Stall",
                "aliases": {"stall", "vendor", "fruit vendor", "awning"},
                "description": "Fresh produce and trail snacks sorted in neat crates.",
                "items": [
                    {"name": "Dried Fruit Pack", "price": 4},
                    {"name": "Clean Water Flask", "price": 3},
                ],
            }
        ],
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
        "visible_npcs": [],
        "points_of_interest": ["Firepit", "Notice tree", "Bench circle"],
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
        "visible_npcs": [],
        "points_of_interest": ["Crest wall", "Trial courtyard"],
    },

    # ── THE ARCHIVE ───────────────────────────────────────────────────────────
    "the_archive": {
        "name": "The Archive",
        "aliases": {"the archive", "archive", "library", "records", "study"},
        "description": (
            "Low ceilings and natural light through narrow windows. Shelves of preserved "
            "materials — printed pages, bound notebooks, salvaged documents. "
            "Someone has organized them obsessively. "
            "Someone else has been through a section near the back recently — "
            "notebooks pulled, a few left open, like they didn't plan on being gone long."
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
        "visible_npcs": ["Archivist"],
        "points_of_interest": ["Trail ledgers", "Disturbed notes stack"],
    },

    # ── THE KEEPER'S DOME ─────────────────────────────────────────────────────
    # The Keeper's Dome. Scene 2 entry point.
    "keepers_dome": {
        "name": "The Keeper's Dome",
        "aliases": {
            "keepers dome", "keeper's dome", "the dome", "dome", "bob",
            "keeper",
        },
        "description": (
            "Low, round, and set back from the path where foot traffic naturally thins. "
            "The outer wall is thick and the door is barely ajar. Something alive moves "
            "inside — you can feel it more than hear it. Not threatening. Present. "
            "The smell is old paper and something warm you can't name. "
            "A ring of attunement marks circles the stone threshold, worn to a shine "
            "from years of people standing in that same spot."
        ),
        "neighbors": ["the_archive", "fence_line", "mystic_trail_trailhead"],
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
        "visible_npcs": ["Keeper Bob (inside)"],
        "points_of_interest": ["Dome door", "Attunement ring", "Route map table"],
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
        "visible_npcs": [],
        "points_of_interest": ["Gate log", "Patrol path"],
    },

    # ── MYSTIC TRAIL ──────────────────────────────────────────────────────────
    "mystic_trail_trailhead": {
        "name": "Mystic Trail Trailhead",
        "aliases": {
            "mystic trail trailhead", "trailhead", "mystic trail", "mystic", "trail", "the trail",
        },
        "description": (
            "The town gives out by degrees here. Low fencing, a weathered trail sign, and a gate "
            "that looks more ceremonial than secure mark the start of Mystic Trail. The air cools "
            "the moment you step under the first reach of canopy. It still feels public. Still close "
            "enough to home. But not fully."
        ),
        "neighbors": ["keepers_dome", "mystic_trail_outer"],
        "interactables": {
            "sign": "A weathered municipal sign bearing Iso Town's crest and the name Mystic Trail. The paint is faded, but someone still clears the moss off it now and then.",
            "gate": "Simple wood and iron. More for guiding foot traffic than stopping anyone.",
            "fence": "Low practical fencing that says this used to be maintained with more confidence than it is now.",
            "canopy": "The branches swallow town light faster than they should.",
        },
        "visible_npcs": [],
        "points_of_interest": ["Trail sign", "Gate", "Canopy edge"],
    },
    "mystic_trail_outer": {
        "name": "Mystic Trail - Outer Stretch",
        "aliases": {"outer trail", "outer", "outer stretch", "mystic outer"},
        "description": (
            "The first stretch of Mystic Trail is clear, packed flat by years of regular use. Benches "
            "sit at uneven intervals, and the path is wide enough that two people could walk side by "
            "side without brushing the ferns. Dust-like motes drift in the angled light and hang a "
            "little longer than they should."
        ),
        "neighbors": ["mystic_trail_trailhead", "mystic_trail_split"],
        "interactables": {
            "bench": "Worn smooth by locals taking a breather on the safer stretch of the trail.",
            "motes": "Dust or pollen, maybe. They drift almost in sync when the air goes still.",
            "path": "Readable, public, familiar. The kind of trail people trust because they've trusted it too long.",
            "trees": "Normal at first glance. A little too quiet if you keep looking.",
        },
        "visible_npcs": [],
        "points_of_interest": ["Trail benches", "Angled canopy light"],
    },
    "mystic_trail_split": {
        "name": "Mystic Trail Split",
        "aliases": {"trail split", "split", "fork", "marker"},
        "description": (
            "A warped wooden marker stands where the trail divides. One branch climbs toward the "
            "overlook above the lake. The other dips lower into damp ground and denser brush. Both "
            "paths are walkable. Neither feels entirely neutral."
        ),
        "neighbors": ["mystic_trail_outer", "mystic_trail_overlook", "mystic_trail_creek_bend"],
        "interactables": {
            "marker": "Old wood split near the base, with hand-cut directional symbols darkened by weather.",
            "left path": "The lower branch bends toward creek country and thicker brush.",
            "right path": "The rise toward the overlook is clearer, more used, and easier to read.",
            "ground": "Two sets of wear patterns. The overlook path gets more foot traffic.",
        },
        "visible_npcs": [],
        "points_of_interest": ["Warped marker", "Overlook branch", "Creek branch"],
    },
    "mystic_trail_overlook": {
        "name": "Mystic Trail Overlook",
        "aliases": {"overlook", "lake overlook", "ridge", "ledge"},
        "description": (
            "The trees open onto a rocky ledge overlooking the lake and the lower tree line beyond it. "
            "Fog lies in pale bands over the water and the distant brush. This is the kind of place "
            "people come to think too long in. The town feels far away from here, even though it isn't."
        ),
        "neighbors": ["mystic_trail_split", "mystic_trail_deep"],
        "interactables": {
            "lake": "Still enough to feel like it's listening.",
            "ledge": "A natural pause point. People have stood here long enough to smooth the stone.",
            "stones": "Good for skipping. Nate's probably thrown half this ledge into the lake over the years.",
            "fog": "It settles over the water in bands, almost like the lake is holding onto old breath.",
            "treeline": "Past the lake and lower growth, the darker stretch of woods suggests where the safer trail ends.",
        },
        "visible_npcs": ["Nate"],
        "points_of_interest": ["Rocky ledge", "Lake view", "Lower treeline"],
    },
    "mystic_trail_creek_bend": {
        "name": "Mystic Trail Creek Bend",
        "aliases": {"creek bend", "creek", "lower branch", "bend"},
        "description": (
            "The lower branch bends along a narrow creek cutting through roots and dark stone. The air "
            "is colder here. Water moves quietly over rock, and the brush crowds closer to the path. "
            "Even the sounds feel dampened."
        ),
        "neighbors": ["mystic_trail_split", "mystic_trail_deep"],
        "interactables": {
            "creek": "The water runs shallow over stone, but the reflections lag strangely when you stare too long.",
            "stones": "Dark, slick, and cold enough to numb your fingers fast.",
            "tracks": "Small prints near the creek bed. Some are ordinary. Some stop where they shouldn't.",
            "branch": "A strip of old cloth is caught here, weathered almost gray.",
        },
        "visible_npcs": [],
        "points_of_interest": ["Narrow creek", "Dark stone", "Deep trail path"],
    },
    "mystic_trail_deep": {
        "name": "Mystic Trail Deep Stretch",
        "aliases": {"deep trail", "deep", "deeper", "deep stretch"},
        "description": (
            "Past the familiar stretch, Mystic Trail narrows into something less maintained. Markers "
            "appear farther apart. Brush leans inward. The fog doesn't sit naturally here — it gathers "
            "with a kind of intention, as if the trail is deciding how much farther it wants to let you go."
        ),
        "neighbors": ["mystic_trail_overlook", "mystic_trail_creek_bend", "mystic_trail_fog_boundary"],
        "interactables": {
            "marker": "Older than the others, half-tilted, and carved with symbols that look more like warnings than directions.",
            "brush": "Close enough now that the trail feels borrowed rather than open.",
            "fog": "It gathers in lanes and pockets that feel directional instead of natural.",
            "silence": "No birds. No insects. Just the sense that sound is being thinned before it reaches you.",
        },
        "visible_npcs": [],
        "points_of_interest": ["Half-tilted marker", "Fog lanes", "Boundary approach"],
    },
    "mystic_trail_fog_boundary": {
        "name": "Mystic Trail Fog Boundary",
        "aliases": {"fog boundary", "fog", "boundary", "forbidden trail", "beyond"},
        "description": (
            "The path ends at a wall of pale, low-hanging fog gathered thick between old posts and "
            "half-rotted warning remnants. The trail continues beyond it, but only in broken glimpses. "
            "Cold clings to the air here. The boundary doesn't look sealed. It looks patient."
        ),
        "neighbors": ["mystic_trail_deep"],
        "interactables": {
            "posts": "Old boundary posts, half-swallowed by moss and time.",
            "warning sign": "Most of the lettering has rotted away. Enough remains to suggest this was once treated like a real boundary.",
            "fog": "It curls and shifts like it's reacting to your attention.",
            "trail beyond": "You can only catch fragments of it through the mist. Just enough to know it keeps going.",
        },
        "visible_npcs": [],
        "points_of_interest": ["Boundary posts", "Rotting warning sign", "Fog wall"],
    },
}
