"""Data-driven narrative choices for Scene 1."""

SCENE_CHOICES = {
    "mom_nate_response": {
        "prompt": "How do you answer her concern about Nate?",
        "options": [
            {
                "id": "dependable",
                "text": "I'll check on him. If he's in trouble, I won't ignore it.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"mom": 1},
                    "disposition": 0,
                    "history": ["mom_nate_dependable"],
                },
                "response_lines": [
                    "She nods once. Relief flickers across her face before she tucks it away.",
                    '"Thank you. That matters."',
                ],
            },
            {
                "id": "dismissive",
                "text": "Nate can handle himself. I don't need to chase him.",
                "effects": {
                    "reputation": -1,
                    "relationships": {"mom": -1},
                    "disposition": 1,
                    "history": ["mom_nate_dismissive"],
                },
                "response_lines": [
                    "Her mouth tightens, not angry — just disappointed.",
                    '"Maybe. But "can" and "should" are different things."',
                ],
            },
            {
                "id": "investigative",
                "text": "What exactly did Bob see? I need context before I move.",
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
        "prompt": "Her words hang there. How do you answer?",
        "options": [
            {
                "id": "receptive",
                "text": "I hear you. I'll stop waiting around and start moving.",
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
                "text": "I'm not fully ready yet, but I'm not pretending anymore.",
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
                "id": "defensive",
                "text": "Everyone keeps pushing me. I'll move when I'm ready.",
                "effects": {
                    "reputation": 0,
                    "relationships": {"mom": -1},
                    "disposition": 1,
                    "history": ["mom_readiness_defensive"],
                },
                "response_lines": [
                    "She looks at you for a long moment, then exhales.",
                    '"Then don\'t confuse delay with a decision."',
                ],
            },
        ],
    },
    "bob_codex_response": {
        "prompt": "Bob sets Nate's Codex in your hands. What do you say?",
        "options": [
            {
                "id": "accept_cleanly",
                "text": "Understood. I'll get this to Nate right now.",
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
                "text": "Why is this urgent? What changed out there?",
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
                "text": "Why me? You've got people with more trail hours.",
                "effects": {
                    "reputation": 0,
                    "relationships": {"bob": -1},
                    "disposition": 1,
                    "history": ["bob_codex_why_me"],
                },
                "response_lines": [
                    '"Because Nate trusts you," Bob says. "And because you needed a first real step."',
                ],
            },
        ],
    },
}
