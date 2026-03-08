from Data.db import getPersonalLeaderboard
from flask import session


def getProfileData(discordID):

    personalLeaderboard = getPersonalLeaderboard(session["discordID"])

    scoresByGame = {}

    for row in personalLeaderboard:
        game = row["gameType"]

        if game not in scoresByGame:
            scoresByGame[game] = {
                "dates": [],
                "scores": []
            }


        scoresByGame[game]["dates"].append(row["timeSubmitted"][:10])  # YYYY-MM-DD
        scoresByGame[game]["scores"].append(row["score"])

    return personalLeaderboard, scoresByGame