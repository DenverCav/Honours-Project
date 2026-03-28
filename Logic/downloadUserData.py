# Logic/score.py

from io import StringIO

import csv

from Data.db import getUserByID, getPersonalLeaderboard


def getUserPersonalScoresAsCSV(discordID):
    user = getUserByID(discordID)
    scores = getPersonalLeaderboard(discordID)
    username = user["username"] if user else "?"
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["username", "game", "score", "date"])

    for score in scores:
        writer.writerow([
            username,
            score.get("gameType"),
            score.get("score"),
            score.get("timeSubmitted")
        ])

    return output.getvalue()
