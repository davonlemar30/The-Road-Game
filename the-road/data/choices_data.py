"""Data-driven narrative choices for Scene 1.

Canon reference: Scene 1 – "Still Here" (ClickUp 86b9b63au)
"""

SCENE_CHOICES = {
    # ── Beat A: Mom asks if you slept okay ───────────────────────────────────
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

    # ── Beat B: How GP responds to Mom's concern about Nate ──────────────────
    "mom_nate_response": {
        "prompt_lines": [
            "She's watching you now.",
            "Waiting to see what you do with what she said.",
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
                    '"Good. Be careful out there."',
                    '"Go see Bob first — he can probably point you in the right direction."',
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
                    "Her mouth tightens, not angry — just tired.",
                    '"Maybe. Go see Keeper Bob."',
                    '"If Nate\'s fine, you lose nothin\' but a walk."',
                    '"If he ain\'t... you\'ll be glad you didn\'t wait."',
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
                    "She studies you for a moment.",
                    '"Fair."',
                    '"He didn\'t say much to me. Just that Nate went out, and he didn\'t like the feel of it."',
                    '"Ask Bob direct. He\'ll tell you what he can."',
                ],
            },
        ],
    },

    # ── Beat C: Optional tone cap — GP's readiness stance ────────────────────
    # Prompt appears after the Nate discussion settles.
    # Canon: 2 options only (receptive / hesitant_honest).
    "mom_readiness_response": {
        "prompt_lines": [
            "She turns back to what she was doing.",
            "But you can feel she's still listening for what you'll do next.",
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
                "text": "I'm just not ready yet. There's nothing out there for me.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"mom": 1},
                    "disposition": -1,
                    "history": ["mom_readiness_honest"],
                },
                "response_lines": [
                    "Her expression stays gentle, but something in her eyes tightens.",
                    '"You really believe that?"',
                    '"That there\'s nothin\' out there for you?"',
                    '"Honey... the world is yours."',
                ],
            },
        ],
    },

    # ── Bob Codex handoff choice ──────────────────────────────────────────────
    "bob_codex_response": {
        "prompt_lines": [
            "The Codex is in your hands now.",
            "Keeper Bob is watching to see how you hold it.",
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
                    'Keeper Bob gives one sharp nod. "Good. Direct and fast."',
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
