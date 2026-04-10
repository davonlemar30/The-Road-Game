"""Data-driven narrative choices for Scene 1."""

SCENE_CHOICES = {
    # ── Opening beat: Mom asks if you slept okay ─────────────────────────────
    "mom_sleep_response": {
        "prompt_lines": [
            "She keeps working. Glances back.",
        ],
        "options": [
            {
                "id": "slept_fine",
                "text": "Slept fine. Yeah.",
                "effects": {
                    "reputation": 0,
                    "relationships": {},
                    "disposition": 0,
                    "history": ["mom_sleep_fine"],
                },
                "response_lines": [
                    '"Mm."',
                ],
            },
            {
                "id": "not_really",
                "text": "Not really.",
                "effects": {
                    "reputation": 0,
                    "relationships": {"mom": 1},
                    "disposition": -1,
                    "history": ["mom_sleep_restless"],
                },
                "response_lines": [
                    '"Yeah."',
                    '"Me neither."',
                ],
            },
            {
                "id": "stay_quiet",
                "text": "[Stay quiet]",
                "effects": {
                    "reputation": 0,
                    "relationships": {},
                    "disposition": 0,
                    "history": ["mom_sleep_quiet"],
                },
                "response_lines": [
                    "She reads the quiet and turns back to the counter.",
                ],
            },
        ],
    },

    # ── How the player responds to Mom's concern about Nate ──────────────────
    "mom_nate_response": {
        "prompt_lines": [
            "She's watching you now.",
            "Not pressing. Just waiting to see what you do with what she said.",
        ],
        "options": [
            {
                "id": "dependable",
                "text": "He's not someone I'd leave hanging. I'll go find him.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"mom": 1},
                    "disposition": 0,
                    "history": ["mom_nate_dependable"],
                },
                "response_lines": [
                    "She nods once. Something in her face settles.",
                    '"Thank you. That matters."',
                ],
            },
            {
                "id": "dismissive",
                "text": "Nate's not fragile. He'll surface when he's ready.",
                "effects": {
                    "reputation": -1,
                    "relationships": {"mom": -1},
                    "disposition": 0,
                    "history": ["mom_nate_dismissive"],
                },
                "response_lines": [
                    "Her mouth tightens, not angry — just noting it.",
                    '"Maybe. But \'can\' and \'should\' aren\'t the same word."',
                ],
            },
            {
                "id": "investigative",
                "text": "What did Bob tell you? I want to know what I'm walking into.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"mom": 0},
                    "disposition": -1,
                    "history": ["mom_nate_investigative"],
                },
                "response_lines": [
                    "She studies you, then nods. You asked the careful question.",
                    '"Fair. Ask Bob direct. He\'ll tell you what he can."',
                ],
            },
        ],
    },
    "mom_readiness_response": {
        "prompt_lines": [
            "She's not pressing it. Just letting it sit there between you.",
        ],
        "options": [
            {
                "id": "receptive",
                "text": "You're right. I've been holding still long enough.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"mom": 1},
                    "disposition": 1,
                    "history": ["mom_readiness_receptive"],
                },
                "response_lines": [
                    "Her shoulders ease. Just a little.",
                    '"That\'s all I needed to hear."',
                ],
            },
            {
                "id": "hesitant_honest",
                "text": "I know I'm not ready. But I'm done pretending I am.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"mom": 1},
                    "disposition": -1,
                    "history": ["mom_readiness_honest"],
                },
                "response_lines": [
                    "She gives a soft, understanding nod.",
                    '"Honest is a good place to start."',
                ],
            },
            {
                "id": "not_there_yet",
                "text": "I hear you. I'm just not there yet.",
                "effects": {
                    "reputation": 0,
                    "relationships": {"mom": -1},
                    "disposition": 0,
                    "history": ["mom_readiness_defensive"],
                },
                "response_lines": [
                    "She gives a small nod. Not satisfied — just accepting.",
                    '"When you are, you\'ll know it."',
                ],
            },
        ],
    },
    "bob_codex_response": {
        "prompt_lines": [
            "The Codex is in your hands now.",
            "Bob is watching to see how you hold it.",
        ],
        "options": [
            {
                "id": "accept_cleanly",
                "text": "I've got it. I'll head out now.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"bob": 1},
                    "disposition": 0,
                    "history": ["bob_codex_accept_cleanly"],
                },
                "response_lines": [
                    'Bob gives one sharp nod. "Good. Direct and fast."',
                ],
            },
            {
                "id": "ask_urgency",
                "text": "What happened out there? I want to understand before I go.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"bob": 0},
                    "disposition": -1,
                    "history": ["bob_codex_ask_urgency"],
                },
                "response_lines": [
                    '"Field\'s noisy and Nate went without his guide," Bob says. "That is urgent."',
                ],
            },
            {
                "id": "why_me",
                "text": "Why not someone with more experience on the Trail?",
                "effects": {
                    "reputation": 0,
                    "relationships": {"bob": -1},
                    "disposition": 0,
                    "history": ["bob_codex_why_me"],
                },
                "response_lines": [
                    '"Because Nate trusts you," Bob says. "And because you needed a first real step."',
                ],
            },
        ],
    },
}
