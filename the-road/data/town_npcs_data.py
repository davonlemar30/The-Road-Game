"""Town NPC dialogue content for the intro vertical slice."""

TOWN_NPC_DIALOGUE: dict[str, dict] = {
    "fruit_vendor": {
        "talk": [
            '"Morning. If you\'re looking for the Keeper, take the Square to the Market, then the Archive."',
            '"His Dome sits just past the stacks. Hard to miss once you smell the paper and ozone."',
        ],
        "hint": "(ask about: keeper  •  nate  •  market)",
        "topics": {
            "keeper": [
                '"Keeper\'s Dome is tucked behind the Archive. Follow the painted signs near the water station."',
            ],
            "nate": [
                '"Saw Nate cut through early yesterday. Looked wired. Headed toward the trail side of town."',
            ],
            "market": [
                '"Market opens fast. If you need supplies before the trail, this is your stop."',
            ],
        },
    },
    "old_guard": {
        "talk": [
            '"You\'re the one Bob asked about, right? He came through here before dawn."',
            '"If it\'s about Nate, don\'t guess. Go ask Bob directly."',
        ],
        "hint": "(ask about: bob  •  danger)",
        "topics": {
            "bob": ['"Archive path, then left. Dome door never really closes."'],
            "danger": ['"Trail edge has felt wrong all week. Don\'t go alone."'],
        },
    },
    "archivist": {
        "talk": [
            '"You\'re late. Bob already asked for those trail ledgers."',
            '"If you need him, follow the corridor to the Dome before he disappears into work again."',
        ],
        "hint": "(ask about: bob  •  trail)",
        "topics": {
            "bob": ['"Keeper\'s Dome is adjacent to the Archive. Through that side path."'],
            "trail": ['"Mystic entries are recent. Nate\'s handwriting appears in the margins."'],
        },
    },
}

