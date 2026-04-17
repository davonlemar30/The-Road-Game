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

    # ── Scene 2: Audri glimpse — who was that? ───────────────────────────────
    # Fires after Bob says "Good timing. I need a favor."
    # Canon reference: Scene 2 – Audri Arrives at the Keeper's Dome (86b9b63aw)
    "audri_who_choice": {
        "prompt_lines": [
            "The door eases shut. The Dome settles back into its quiet.",
        ],
        "options": [
            {
                "id": "who_was_that",
                "text": "Who was that?",
                "effects": {
                    "reputation": 0,
                    "relationships": {},
                    "disposition": 0,
                    "history": ["asked_about_audri"],
                },
                "response_lines": [
                    "Bob glances toward the door. A small pause.",
                    '"Audri. Came back through yesterday — all five Crests."',
                    '"Finished a full circuit. You don\'t see that often."',
                    "He turns back to the table.",
                    '"You\'ll meet her properly. But that\'s not why I called you in."',
                ],
            },
            {
                "id": "focus_forward",
                "text": "I'll hear the favor.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"bob": 1},
                    "disposition": 0,
                    "history": ["skipped_audri_question"],
                },
                "response_lines": [
                    'Bob nods once. "Good instinct."',
                ],
            },
            {
                "id": "stay_quiet_dome",
                "text": "[Stay quiet]",
                "effects": {
                    "reputation": 0,
                    "relationships": {},
                    "disposition": 0,
                    "history": ["stayed_quiet_dome"],
                },
                "response_lines": [
                    "He reads the silence. Sets down his tools.",
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

    # ── Scene 3: Lake Ambush at the Overlook ─────────────────────────────────
    # Canon reference: Scene 3 – Nate at the Mystic Trail Overlook (ClickUp)
    # Hidden-state only: outcomes identical, deltas shape later scenes.

    # Beat 1 — Nate gasps the warning before Murkmind reveals itself.
    "nate_ambush_response": {
        "prompt_lines": [
            "Nate's breath rattles. His hand trembles toward the fog.",
            "\"Run,\" he manages. \"It's still here.\"",
        ],
        "options": [
            {
                "id": "stay_with_nate",
                "text": "I'm not leaving you. Stay down.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"nate": 1},
                    "disposition": -1,
                    "history": ["scene3_stay_with_nate"],
                },
                "response_lines": [
                    "You plant yourself between him and the fog.",
                ],
            },
            {
                "id": "face_the_threat",
                "text": "Where is it? I'll meet it.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"nate": 0},
                    "disposition": 1,
                    "history": ["scene3_face_the_threat"],
                },
                "response_lines": [
                    "You step forward, eyes hunting the ridge line.",
                ],
            },
            {
                "id": "freeze_at_warning",
                "text": "[Freeze — the word doesn't land.]",
                "effects": {
                    "reputation": 0,
                    "relationships": {"nate": 0},
                    "disposition": -1,
                    "history": ["scene3_freeze_at_warning"],
                },
                "response_lines": [
                    "Your legs lock. The fog keeps moving.",
                ],
            },
        ],
    },

    # Beat 2 — Mid-battle pressure spike, before the Switch pulse fires.
    "murkmind_pressure_response": {
        "prompt_lines": [
            "Pressure rings the overlook. Your thoughts skid.",
            "Nate coughs, blood on his teeth.",
        ],
        "options": [
            {
                "id": "anchor_on_nate",
                "text": "[Anchor on Nate. Keep him breathing.]",
                "effects": {
                    "reputation": 1,
                    "relationships": {"nate": 1},
                    "disposition": -1,
                    "history": ["scene3_anchor_on_nate"],
                },
                "response_lines": [
                    "You lock onto his voice and the spike loses its edge.",
                ],
            },
            {
                "id": "lock_into_survival",
                "text": "[Lock into the fight. One clean read.]",
                "effects": {
                    "reputation": 1,
                    "relationships": {"nate": 0},
                    "disposition": 1,
                    "history": ["scene3_lock_into_survival"],
                },
                "response_lines": [
                    "The noise flattens to a single line. You read the next move.",
                ],
            },
            {
                "id": "push_back_angrily",
                "text": "[Shove the pressure back with spite.]",
                "effects": {
                    "reputation": 0,
                    "relationships": {"nate": 0},
                    "disposition": 2,
                    "history": ["scene3_push_back_angrily"],
                },
                "response_lines": [
                    "Heat flares in your chest. The fog recoils a step.",
                ],
            },
        ],
    },

    # Beat 3 — Capture just sealed. Murkmind is down, Nate is still down.
    "post_capture_priority": {
        "prompt_lines": [
            "The Cube stops rattling. The overlook is quiet.",
            "Nate hasn't moved.",
        ],
        "options": [
            {
                "id": "check_nate_first",
                "text": "Nate first. Cube can wait.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"nate": 1},
                    "disposition": -1,
                    "history": ["scene3_check_nate_first"],
                },
                "response_lines": [
                    "You drop beside him. His pulse is there — faint, but there.",
                ],
            },
            {
                "id": "study_cube_first",
                "text": "Lift the Cube. Understand what just happened.",
                "effects": {
                    "reputation": 0,
                    "relationships": {"nate": 0},
                    "disposition": 0,
                    "history": ["scene3_study_cube_first"],
                },
                "response_lines": [
                    "The Cube is warm. Something is alive inside it.",
                ],
            },
            {
                "id": "check_nate_astari_too",
                "text": "Check Nate. Then check his Astari.",
                "effects": {
                    "reputation": 1,
                    "relationships": {"nate": 1},
                    "disposition": 0,
                    "history": ["scene3_check_nate_astari_too"],
                },
                "response_lines": [
                    "His pulse holds. His Astari is curled beside him, still breathing.",
                ],
            },
        ],
    },

    # ── Scene 4: Nate recovery at camp ──────────────────────────────────────
    "audri_interest_response": {
        "prompt_lines": [
            "Nate studies your face through the fire-shadow.",
            "\"I know that look,\" he says, voice rough. \"What's her name?\"",
        ],
        "options": [
            {
                "id": "deflect",
                "text": "Don't do this right now, Nate.",
                "effects": {
                    "reputation": 0,
                    "relationships": {"nate": 0},
                    "disposition": -1,
                    "history": ["scene4_audri_deflect"],
                },
                "response_lines": [
                    "Nate snorts softly. \"Yeah, fair.\"",
                ],
            },
            {
                "id": "stay_quiet",
                "text": "[Stay quiet.]",
                "effects": {
                    "reputation": 0,
                    "relationships": {"nate": 0},
                    "disposition": 0,
                    "history": ["scene4_audri_silence"],
                },
                "response_lines": [
                    "You let the quiet answer. Nate doesn't push.",
                ],
            },
            {
                "id": "admit_it",
                "text": "Audri. I don't know what it is yet, but yeah.",
                "effects": {
                    "reputation": 0,
                    "relationships": {"nate": 1},
                    "disposition": 0,
                    "history": ["scene4_audri_admitted"],
                },
                "response_lines": [
                    "\"Knew it,\" Nate says, half-smiling despite the pain.",
                ],
            },
        ],
    },
    "dreamleaf_motivation": {
        "prompt_lines": [
            "Nate nods toward the darker trail.",
            "\"Dreamleaf's out there. Why are you really going after it?\"",
        ],
        "options": [
            {
                "id": "for_audri",
                "text": "For Audri. I want to show up with something real.",
                "effects": {
                    "reputation": 0,
                    "relationships": {},
                    "disposition": 0,
                    "history": ["scene4_dreamleaf_for_audri"],
                },
                "response_lines": [
                    "\"Then don't fake it,\" Nate says. \"Bring back the real thing or don't pretend.\"",
                ],
            },
            {
                "id": "prove_something",
                "text": "To prove I can do this.",
                "effects": {
                    "reputation": 0,
                    "relationships": {},
                    "disposition": 1,
                    "history": ["scene4_dreamleaf_self_worth"],
                },
                "response_lines": [
                    "\"Good,\" Nate says. \"Make it about your feet, not anyone else's eyes.\"",
                ],
            },
            {
                "id": "murkmind_training",
                "text": "For Murkmind training. We need field reps, not theory.",
                "effects": {
                    "reputation": 0,
                    "relationships": {},
                    "disposition": 0,
                    "history": ["scene4_dreamleaf_murkmind_training"],
                },
                "response_lines": [
                    "Murkmind's casing gives a low, steady pulse beside your boot.",
                ],
            },
        ],
    },
}
