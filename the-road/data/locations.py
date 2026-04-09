"""Static location content for Scene One of The Road.

All inspect text sourced from GP's House (ClickUp canon).
Descriptions are revealed only when the player uses 'look'.
"""

LOCATIONS = {
    "bedroom": {
        "name": "Bedroom",
        "description": (
            "Warm and still. The ceiling fan ticks on its slowest setting. "
            "A TV on the dresser, PS5 underneath it — controller cord dangling. "
            "A gaming computer in the corner, fan humming even now. "
            "Books you've half-read, notes you've half-started. "
            "You've been in this same groove long enough that the floor knows your footsteps."
        ),
        "exits": {"south": "living_room"},
        "interactables": {
            "mirror": (
                "Tape marks where old notes used to be. "
                "You can almost remember what they said. Almost."
            ),
            "bookshelf": (
                "Spines you've reread enough to memorize. "
                "The new ones still look too clean."
            ),
            "window": (
                "Outside is louder than you want it to be. "
                "You keep the curtains half-closed like a compromise."
            ),
            "chair": (
                "Three layers of clothes you meant to hang up. "
                "The oldest ones are from a version of you that had a plan."
            ),
            "bed": (
                "Rumpled blankets. Not slept-in so much as inhabited. "
                "You've been here a long time."
            ),
            "tv": (
                "A decent-sized flatscreen, older but still good. "
                "The PS5 underneath has a faint blue light — on standby. "
                "Controller on the floor where you left it. "
                "The game hasn't saved in a while."
            ),
            "ps5": (
                "Blue standby light. You've put more hours into it than you'd admit. "
                "Lately it just sits there."
            ),
            "computer": (
                "A mid-tier gaming rig, built piece by piece. The fan hums constantly. "
                "The monitor is dark but a browser tab is still open from last night. "
                "You can inspect it closer. Type 'inspect notes' to read what's on the screen."
            ),
            "notes": (
                "A browser tab left open: a forum thread titled 'Astari bonding — what nobody tells you.' "
                "Below it, a text doc you started yourself:\n\n"
                "  > Astari aren't just for travel. Read three separate accounts now.\n"
                "  > Something about the bond changes the way you think — not the thoughts,\n"
                "  > but the *speed*. Like having backup processing.\n"
                "  > The Keeper's Dome is the closest place. He's been asking about me apparently.\n"
                "  > Keep putting it off. Don't know why.\n\n"
                "The doc is dated three weeks ago."
            ),
        },
    },

    "living_room": {
        "name": "Living Room",
        "description": (
            "The curtains are half-drawn. A lamp burns soft gold even in the morning. "
            "The TV glows in the corner — old pre-collapse programming on a loop, "
            "signal that never stopped coming through. "
            "Your mom's chair faces it. It's warm in here. It's a little too warm in here."
        ),
        "exits": {
            "north": "bedroom",
            "east": "kitchen",
            "south": "front_door",
        },
        "interactables": {
            "tv": (
                "Old pre-collapse programming runs on repeat. "
                "Nobody knows why the signal still comes through. "
                "Maybe no one remembers how to turn it off."
            ),
            "photo": (
                "Everyone is smiling like it cost nothing. "
                "The frame is still here. The moment isn't."
            ),
            "couch": (
                "A throw blanket folded at one end — Mom's. "
                "Your end of the cushion is worn in. Comfort and cage aren't always different things."
            ),
            "shelf": (
                "Family things that haven't been looked at in a while. "
                "Kept, not celebrated. There's a difference."
            ),
            "stairs": (
                "The banister is worn smooth from years of the same hand on the same path. "
                "Upstairs is yours. Downstairs is shared. The landing is the in-between."
            ),
        },
    },

    "kitchen": {
        "name": "Kitchen",
        "description": (
            "Small. Practical. A kettle that's already been run this morning — "
            "she was up before you. Two mugs: one clean in the rack, one left to the side. "
            "A list on the counter in her handwriting."
        ),
        "exits": {"west": "living_room"},
        "interactables": {
            "kettle": (
                "Still warm. She had hers hours ago. "
                "Cold metal. You can almost hear mornings that started better."
            ),
            "list": (
                "Bills. Errands. Reminders. "
                "Love written in bullet points."
            ),
            "mug": (
                "Two mugs. One is hers — worn handle, tea-stained inside. "
                "The other is yours. Sometimes clean. Sometimes not."
            ),
            "pantry": (
                "Practical staples. Nothing indulgent. "
                "Enough to last, not enough to get comfortable."
            ),
        },
    },

    "front_door": {
        "name": "Front Door",
        "description": (
            "The door is reinforced and heavy, built to hold something back. "
            "Through the gap at the bottom you can feel the street — cooler, sharper, different. "
            "A small porch. A wind chime that barely moves. "
            "The yard patch beyond has something struggling to grow."
        ),
        "exits": {
            "north": "living_room",
            "out": "outside",
        },
        "interactables": {
            "door": (
                "The lock clicks softly when you test it. "
                "It's not locked against you. It never was."
            ),
            "charm": (
                "A small charm etched with a curled symbol — like a crest, "
                "but worn smooth. Not from around here. Not from your side of town."
            ),
            "planter": (
                "Something green and small pushing up through packed soil. "
                "It doesn't know it's supposed to struggle. It's just growing."
            ),
            "wind chime": (
                "Barely moving. The street air is still this morning. "
                "It makes sound sometimes. Right now it's just waiting."
            ),
        },
    },
}
