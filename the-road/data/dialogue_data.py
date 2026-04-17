"""Dialogue content for Scene One: 'Still Here'."""

# Mom's blessing — plays when player tells mom they're heading out (forbidden trail / plan)
# Triggers told_mom_plans + phone handoff
MOM_BLESSING = [
    "She goes quiet for a second. Just a second.",
    '"So you\'re really going."',
    "Not a question. She already knew.",
    '"Alright. Then listen to me."',
    '"You already came back with an Astari. Murkmind chose you in blood and fog."',
    '"That does not make the Forbidden Trail safe. It makes you less alone."',
    '"You still go through Keeper Bob before you step deeper. I mean it."',
    "She disappears into the kitchen. Comes back with an old phone in her hand.",
    "Screen scratched. Worn at the corners.",
    '"Take this. It\'s got a map of Iso Town and some of Bob\'s field notes on it."',
    '"Passphrase on the notes is locked — Bob\'ll give you the code when you pick up your Astari."',
    '"Check in when you can."',
    "A beat. She doesn't say anything else.",
    '"Go."',
]

MOM_BLESSING_HINT = "(You have Mom's old phone. Head back to the Keeper's Dome when you're ready.)"

# Mom's opening — up to and including "You sleep okay?"
# Followed by the sleep-response choice before the rest of the scene.
MOTHER_SCENE1_PART1 = [
    '"Mornin\', baby."',
    "She's at the counter. A cloth in her hand. The kettle's already run — she's been up a while.",
    '"You sleep okay?"',
]

# Mom's main news — plays after the player responds to "You sleep okay?"
# Voice: warm, Southern-inflected, tired but loving. Present before practical.
# Canon reference: Scene 1 – Prologue: "Still Here" (ClickUp 86b9b63au)
MOTHER_SCENE1_PART2 = [
    '"Keeper Bob stopped by earlier,"',
    "She keeps working, correcting herself without thinking.",
    '"He was lookin\' for that friend of yours. Nate."',
    "A pause. She sets the cloth down.",
    '"Bob wasn\'t angry. He just looked... worried. Which is unlike him."',
    "She finally glances up at you.",
    '"Go check on him," she says. "See if there\'s anything you can do."',
    "Then, softer:",
    '"And if you go pokin\' around that trail... just be careful out there, honey."',
    '"That place been feelin\'... off lately."',
]

# Kept for reference; no longer used in the active scene flow.
MOTHER_SCENE1 = MOTHER_SCENE1_PART1 + MOTHER_SCENE1_PART2

# Hint shown after the opening scene — plain, conversational.
MOTHER_SCENE1_HINT = "She's here if there's more on your mind."

# Dismissal lines — after scene1 dialogue is done, repeated talks
MOTHER_AFTER = [
    'She nods toward the door. "Go while you still mean it."',
]

# ─── Q & A TREE ─────────────────────────────────────────────────────────────
# Keys: topic slug (used by `ask mom <topic>`)
# Each entry: {answer: list[str], followups: dict[str, list[str]], hint: str}
#
# Naming: top-level = "nate", subquestion = "nate trail" / "nate trouble" etc.
# ─────────────────────────────────────────────────────────────────────────────

MOM_QA: dict[str, dict] = {

    # ── NATE ─────────────────────────────────────────────────────────────────
    "nate": {
        "answer": [
            '"Nate?"',
            "She almost smiles. Almost.",
            '"Baby, you know that boy better than I do."',
            '"Y\'all been runnin\' that same trail since middle school."',
            '"But lately he\'s been... somewhere else, even when he\'s standing right here."',
            '"He\'s got fire. Always has. Just needs someone who can think a step ahead of it."',
            '"Right now that might need to be you."',
        ],
        "hint": "",
        "followups": {
            "nate trail": [
                '"The Mystic Trail?"',
                '"Y\'all used to go up there to goof around when you were little."',
                '"But that trail connects to the Forbidden Trail now."',
                '"And that ain\'t a place for foolishness — not without the right preparation."',
                '"I mean it."',
            ],
            "nate trouble": [
                "She sets down the mug she's been holding.",
                '"I don\'t know exactly. That\'s what worries me."',
                '"Keeper Bob was on my porch before sunrise. He doesn\'t do that."',
                '"Whatever it is, it was enough to send him here instead of waiting."',
                '"That tells me enough."',
            ],
            "nate dangerous": [
                '"Nate is bold. Always has been."',
                '"Bold ain\'t the same as ready."',
                "A pause. She's choosing her next words.",
                '"Go check on him. But don\'t let his energy pull you somewhere you\'re not built for yet."',
                '"You\'re not him. That\'s not a bad thing."',
            ],
        },
    },

    # ── ASTARI ───────────────────────────────────────────────────────────────
    "astari": {
        "answer": [
            "She leans against the counter. Takes her time with this one.",
            '"An Astari is... hard to explain if you haven\'t felt it yourself."',
            '"They\'re not pets. Not tools. It\'s more like — they fill in the part of you that goes quiet under pressure."',
            '"The world out there — the roads, the trails between towns — it\'s rougher than it used to be. Not built for people going alone."',
            '"An Astari changes that."',
        ],
        "hint": "",
        "followups": {
            "astrali bond": [
                '"The bond isn\'t something that just happens."',
                '"The Astari reads you first — your field, your intent. Decides whether there\'s something worth committing to."',
                '"Then you grow into it together. Some people never do it right and spend years wondering why things keep slipping."',
                '"It runs both ways. That\'s what makes it real."',
            ],
            "astrali dangerous": [
                '"Without one out there? You\'re exposed."',
                '"That\'s just the truth. I\'m not saying it to scare you."',
                '"Nate has one. Most people your age who move around have at least started."',
                '"You\'ve waited longer than most."',
            ],
            "astrali get": [
                '"Keeper Bob keeps a few at the Keeper\'s Dome."',
                '"Has for years. He\'s been asking when you were coming in to choose."',
                '"He mentioned you specifically, more than once."',
                'A small pause. "Maybe now\'s the time."',
            ],
            "no astrali": [
                "She goes quiet.",
                '"I had a chance once. I said no because staying felt safer."',
                '"Some days I still think I chose right. Some days I know I didn\'t."',
                '"I don\'t want fear making your choices for you the way it made mine."',
            ],
        },
    },

    # ── OUTSIDE / DANGER ─────────────────────────────────────────────────────
    "outside": {
        "answer": [
            '"It\'s not like it used to be."',
            '"The routes between towns are rougher. There are things in the stretches that don\'t care who you are."',
            '"The Crests help — they signal that you\'ve been tested, that you carry yourself a certain way."',
            '"But you don\'t have one yet. So you go careful."',
        ],
        "hint": "",
        "followups": {
            "outside crests": [
                '"Crests are how people read you out there."',
                '"Not just status — it\'s practical. Some doors stay closed without them."',
                '"Certain paths are blocked. Even some Astari respond differently to Crest-holders."',
                '"Caldren Vale runs the local trial, down at the Foundation Steps, if you ever want to know more."',
                '"He\'s... exacting. But fair."',
            ],
            "outside town": [
                '"Iso Town is steady."',
                '"Keeps to itself. Protected enough."',
                "A quieter beat.",
                '"But steady and good aren\'t always the same thing, baby."',
                '"I know that better than most."',
            ],
            "outside collapse": [
                '"Things changed years back."',
                '"The world didn\'t end — it just... settled differently."',
                '"Some places are fine. Others aren\'t. Some are fine on the surface."',
                '"You learn which is which the longer you move through it."',
                '"That\'s why you need people — and an Astari — you can trust."',
            ],
        },
    },

    "bob said": {
        "answer": [
            '"Mostly what I told you."',
            '"Nate had been pulling field ledgers on the outer trails. Asking about the Mystic-Forbidden split. Sharp questions, Bob said."',
            '"Then three days ago — gone. Left in the middle of something, from the look of it."',
            '"Bob mentioned something else, too. Said the Field\'s been noisy lately."',
            "A small pause.",
            '"I didn\'t push him on what that meant. But he looked like a man who\'d slept on a bad feeling."',
        ],
        "hint": "",
        "followups": {},
    },

    "dangerous": {
        "answer": [
            '"Yes. More than folks say out loud."',
            '"Not every danger looks like teeth. Some of it feels like bad weather in your bones."',
            '"That\'s why I keep saying: get informed, get partnered, then move."',
        ],
        "hint": "",
        "followups": {},
    },

    # ── FORBIDDEN TRAIL / PLAYER'S PLAN ─────────────────────────────────────
    # Asking about the forbidden trail or telling mom you're going triggers the blessing.
    # Handled specially in dialogue.py — this entry is a fallback hint only.
    "forbidden trail": {
        "answer": [
            '"You want to go in there."',
            "Again — not a question.",
            '"Then say it. Tell me you\'re going."',
        ],
        "hint": "Try telling her directly.",
        "followups": {},
    },

    # ── PROFESSOR BOB ────────────────────────────────────────────────────────
    "bob": {
        "answer": [
            '"Keeper Bob\'s been here longer than most people remember."',
            '"Keeps the Dome running almost by himself. Good man — disorganized, but good."',
            '"He had a couple Astari in there he was holding for students who never showed up."',
            '"Then this morning he\'s knocking on my door before I\'ve even had my coffee."',
            '"Looking like he hadn\'t slept. Asking about Nate."',
        ],
        "hint": "",
        "followups": {
            "bob dome": [
                '"The Keeper\'s Dome, down near the edge of town."',
                '"You\'ve walked past it a hundred times."',
                '"Smells like old paper and something alive."',
                '"He keeps odd hours, but the door\'s usually unlocked."',
            ],
            "bob nate": [
                '"He wouldn\'t say too much. Said Nate had been coming in asking questions."',
                '"Then just... stopped. Took some of Bob\'s field notes with him."',
                "She shakes her head slowly.",
                '"Bob didn\'t look happy about it. But he was more worried than angry."',
            ],
            "bob astari": [
                '"He\'d probably set you up with one today if you walked in and asked."',
                '"He\'s been trying to get you in there for a while now."',
                '"Said something once — \'some people are ready before they know it.\'"',
                '"Might be worth finding out if he was right."',
            ],
        },
    },
}
