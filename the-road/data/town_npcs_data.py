"""Town NPC dialogue content for the intro vertical slice."""

TOWN_NPC_DIALOGUE: dict[str, dict] = {
    "fruit_vendor": {
        "talk": [
            '"Early for wandering."',
            "She stacks a crate without looking up. Something rust-colored. Efficient hands.",
            '"You lost, or just thinking?"',
        ],
        "hint": "",
        "topics": {
            "keeper": [
                '"Bob? Through the Market, past the Archive, then you\'ll smell it before you see it."',
                '"Old paper and something warm. Always on. He never really closes up."',
            ],
            "nate": [
                '"Came through early yesterday. Moving like something was chasing him — or like he was chasing something."',
                '"Headed toward the back fence."',
            ],
            "market": [
                '"You\'re standing in it."',
                '"What do you need?"',
            ],
            "trail": [
                '"Mystic? People go."',
                '"Forbidden?"',
                "A beat.",
                '"People go there too. Not always the same ones that come back."',
            ],
        },
    },
    "old_guard": {
        "talk": [
            "He watches you for a beat before he speaks.",
            '"Bob came through before dawn. That\'s not a man who moves early unless something needs moving."',
            '"If you\'re headed to the Dome — yeah. That\'s probably where you should be."',
        ],
        "hint": "",
        "topics": {
            "bob": [
                '"Been in this town forty years. Seen him move early maybe three times."',
                '"Archive path, then left. Dome door stays cracked. You\'ll know when you\'re there."',
            ],
            "nate": [
                '"Nate."',
                "A long pause. He looks at the fence line.",
                '"Moves like he\'s got something to prove. Nothing wrong with that, till it is."',
            ],
            "danger": [
                '"Trail edge has been off all week. Can\'t tell you what it is. Just feels wrong."',
                '"The Field gets that way sometimes. Means something\'s moved that shouldn\'t have."',
            ],
            "fence": [
                '"Fence has held longer than most people remember."',
                '"Stay inside it till you know what you\'re doing on the other side."',
            ],
        },
    },
    "archivist": {
        "talk": [
            "They don't look up. Reading something, pages spread flat.",
            '"Looking for Bob, or just browsing?"',
            "A half-second pause.",
            '"If it\'s Bob — Dome is through that side door. He\'s been in since early."',
        ],
        "hint": "",
        "topics": {
            "bob": [
                '"Dome\'s adjacent. That side path."',
                '"Knock, but don\'t wait long. He doesn\'t hear things when he\'s mid-thought."',
            ],
            "trail": [
                '"Mystic trail records are in the third shelf — outer east section."',
                '"They\'ve had a lot of traffic recently. Check the margins if you want the interesting parts."',
            ],
            "nate": [
                '"Someone came through and pulled three field notebooks. Left them half-open on the table."',
                "They nod toward the disturbed section near the back.",
                '"Didn\'t sign the log. I know his handwriting anyway."',
            ],
            "ledgers": [
                '"Outer trail ledgers?"',
                '"Back section. Someone beat you to them."',
                '"Left notes in the margins. Might be worth reading before you decide to follow."',
            ],
        },
    },
}

