# I know this does not make sense in the slightest without context, but the Tetris.com competitive community
# split up the category in an informal way to add in tiers. This is why I called it arbitrary
# even though that's what it's called by the community.

def getArbitraryTiers(game, score):
    if score is None:
        return None

    try:
        score = int(score)
    except (ValueError, TypeError):
        return None

    tiers = {
    "Tetris.com": [

        ("Tier 1", 1_500_000),

        ("Tier 2", 2_000_000),

        ("Tier 3", 2_500_000),

        ("Tier 4", 3_000_000),

        ("Tier 5", 3_500_000),

        ("Tier 6", 4_000_000),

    ],

    "MindBender": [

        ("Tier 1", 1_000_000),

        ("Tier 2", 1_250_000),

        ("Tier 3", 1_500_000),

        ("Tier 4", 1_750_000),

        ("Tier 5", 2_000_000),

    ],

    "E60": [

        ("Tier 1", 100_000),

        ("Tier 2", 150_000),

        ("Tier 3", 175_000),

        ("Tier 4", 200_000),

        ("Tier 5", 225_000),

        ("Tier 6", 250_000),

    ],

    "NBlox": [

        ("Tier 1", 1_000_000),

        ("Tier 2", 1_400_000),

        ("Tier 3", 1_600_000),

        ("Tier 4", 1_800_000),

        ("Tier 5", 2_000_000),

        ("Tier 6", 3_000_000),  # I don't know what the B125B scores would be, so I'm going with this

    ],
}

    gameList = {
        "Tetris.com (Untuned)": "Tetris.com",
        "Tetris.com (Tuned)": "Tetris.com",
        "MindBender": "MindBender",
        "E60": "E60",
        "NBlox": "NBlox"
    }

    ruleKey = gameList.get(game)

    if not ruleKey:
        return None

    for tier, threshold in reversed(tiers[ruleKey]):
        if score >= threshold:
            return tier