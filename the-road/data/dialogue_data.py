"""Dialogue content for Scene One: 'Still Here'."""

# Mom's main monologue — plays on first talk, Scene 1
# Voice: warm, Southern-inflected, tired but loving. She checks practical things first.
MOTHER_SCENE1 = [
    '"Mornin\', baby. You sleep okay?"',
    "She doesn't wait for an answer. Already moving, already managing.",
    '"Professor Bob stopped by lookin\' for that friend of yours — Nate."',
    '"Said he ain\'t seen him in a couple days. You heard from him?"',
    "A pause. The kettle clicks off.",
    '"Well... maybe go poke around that lil spot y\'all always end up at. You know the one."',
    '"Wouldn\'t hurt to stretch them legs and give that damn game a break."',
    "She looks at you properly now. A beat longer than usual.",
    '"It\'s not safe out there without an Astari, baby."',
    '"You can\'t keep leanin\' on other people forever."',
    '"Just... be careful if you go lookin\' for him, alright?"',
]

# Shown after Mom's monologue — prompts the player
MOTHER_SCENE1_PROMPT = (
    "\nMom is still nearby. You can ask her things if you want.\n"
    "  ask mom nate       — about Nate\n"
    "  ask mom astari     — about Astari\n"
    "  ask mom outside    — about what's out there\n"
    "  ask mom bob        — about Professor Bob\n"
)

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
            '"Baby, you know Nate better than I do."',
            '"Y\'all been running that same trail since middle school."',
            '"But lately he\'s been... different. Pushing into places he shouldn\'t."',
            '"That boy has a lot of fire and not enough sense to point it anywhere safe."',
            '"Somebody needs to go check on him before he does something he can\'t walk back."',
        ],
        "hint": "  ask mom nate trail | ask mom nate trouble | ask mom nate dangerous",
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
                '"Professor Bob was on my porch before sunrise. He doesn\'t do that."',
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
            "She leans against the counter. This one she takes seriously.",
            '"An Astari is... hard to explain if you haven\'t bonded with one."',
            '"They\'re companions. Survival partners, really."',
            '"The world out there — the roads, the trails between towns — it\'s not built for people traveling alone anymore."',
            '"Having an Astari changes that."',
        ],
        "hint": "  ask mom astari bond | ask mom astari dangerous | ask mom astari get",
        "followups": {
            "astari bond": [
                '"Bonding takes time. It\'s not like picking up a tool."',
                '"You grow into it together. Some people never do it right and wonder why everything keeps going wrong."',
                '"It\'s a commitment, not just a convenience."',
            ],
            "astari dangerous": [
                '"Without one out there? You\'re exposed."',
                '"That\'s just the truth. I\'m not saying it to scare you."',
                '"Nate has one. Most people your age who move around have at least started."',
                '"You\'ve waited longer than most."',
            ],
            "astari get": [
                '"Professor Bob keeps a few at his lab."',
                '"Has for years. He\'s been asking when you were coming in to choose."',
                '"He mentioned you specifically, more than once."',
                'A small pause. "Maybe now\'s the time."',
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
        "hint": "  ask mom outside crests | ask mom outside town | ask mom outside collapse",
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

    # ── PROFESSOR BOB ────────────────────────────────────────────────────────
    "bob": {
        "answer": [
            '"Professor Bob\'s been here longer than most people remember."',
            '"Keeps that lab running almost by himself. Good man — disorganized, but good."',
            '"He had a couple Astari in there he was holding for students who never showed up."',
            '"Then this morning he\'s knocking on my door before I\'ve even had my coffee."',
            '"Looking like he hadn\'t slept. Asking about Nate."',
        ],
        "hint": "  ask mom bob lab | ask mom bob nate | ask mom bob astari",
        "followups": {
            "bob lab": [
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
