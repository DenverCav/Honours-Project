from Logic.score import processScoreSubmission


def test_valid_personal_score():
    status, message, redirect = processScoreSubmission(

        discordID="123",

        username="testuser",

        isAdmin=False,

        game="Tetris.com (Untuned)",

        score=100000,

        destination="personal",

        notes="test",

        date_achieved=None,

        player_name="testuser",

        link=""

    )

    assert status == "success"


def test_invalid_negative_score():
    status, message, redirect = processScoreSubmission(

        discordID="123",

        username="testuser",

        isAdmin=False,

        game="Tetris.com (Untuned)",

        score=-1,

        destination="personal",

        notes="test",

        date_achieved=None,

        player_name="testuser",

        link=""

    )

    assert status != "success"


def test_missing_game():
    status, message, redirect = processScoreSubmission(

        discordID="123",

        username="testuser",

        isAdmin=False,

        game=None,

        score=1000,

        destination="personal",

        notes="",

        date_achieved=None,

        player_name="testuser",

        link=""

    )

    assert status != "success!"