from Data.db import (submitOfficialLeaderboard, submitPersonalScores, deleteExactScore, deletePersonalScoreForUser)

minimumScores = {
    "Tetris.com": 1500000,
    "MindBender": 500000,
    "E60": 100000,
    "NBlox": 1000000
}


def processScoreSubmission(
        discordID, username, isAdmin, game, score, destination, notes, date_achieved,player_name, link):

    if not game or score is None:
        return ("warning", "Please fill in all required fields", "submitScore")

    if score is None or score < 0:
        return "error", "Invalid score", None

    if isAdmin and destination == "official":

        if game in minimumScores and score < minimumScores[game]:
            return ("warning", f"The score does not meet the minimum for {game}", "submitScore")

        if not player_name or not link:
            return ("warning", "Admin submissions require a player name and a proof link", "submitScore")

        submitOfficialLeaderboard(
            username=player_name,
            score=score,
            link=link,
            gameType=game,
            submittedBy=username,
            notes=notes
        )

        return ("success", "Score submitted to official leaderboard!", "leaderboard")

    submitPersonalScores(
        discordID=discordID,
        score=score,
        gameType=game,
        notes=notes,
        date_achieved=date_achieved
    )

    return ("success", "Score added to your personal profile!", "profile")


def processScoreDeletion(username, game, score):
    deleted = deleteExactScore(
        username=username,
        gameType=game,
        score=score
    )

    return deleted


def processPersonalScoreDeletion(discordID, scoreID):
    return deletePersonalScoreForUser(discordID, scoreID)

