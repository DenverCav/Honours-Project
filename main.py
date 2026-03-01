import os, csv
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # For local tessting
from flask import Flask, render_template, redirect, url_for, session, request, flash, make_response
from flask_dance.contrib.discord import make_discord_blueprint, discord
from dotenv import load_dotenv
from io import StringIO
from Data.db import createDB, getUserByID, insert_user, getDebug, submitOfficialLeaderboard, getLeaderboardFromGame, getAllGames, getPersonalLeaderboard, submitPersonalScores, getAllUsers, deleteExactScore, getUserScoreTimeline, deletePersonalScoreForUser, permanentlyDeleteUser, markUserForDeletion, getBestScoresByPlayer # My database helper functions
load_dotenv()
from Logic.auth import loginUser, logoutUser
from Logic.session import createUser
from Logic.isAdmin import ADMIN_IDS, checkAdmin
from Logic.arbitraryClub import getArbitraryTiers


app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Session encryption
# --- OAuth2 Setup ---
discord_bp = make_discord_blueprint(
   client_id=os.getenv("DISCORD_CLIENT_ID"),
   client_secret=os.getenv("DISCORD_CLIENT_SECRET"),
   scope="identify",
   redirect_url="/login/complete" # I forgot to add this line in originally and always wondered why
    # the login button needed to be clicked twice
)


app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    )

app.register_blueprint(discord_bp, url_prefix="/login")

# Initialises the database
#createDB()
@app.context_processor # This injects variables automatically into templates
def createUser():
   if "discordID" in session:
       return {
           "logged_in": True,
           "username": session.get("username"),
           "user_pfp": session.get("avatarURL"),
           "is_admin": checkAdmin(session["discordID"])
       }
   return {
       "logged_in": False,
       "username": None,
       "user_pfp": None,
       "is_admin": False
   }

# --- Routes ---
@app.route("/")
def home():
   return render_template("home.html")


@app.route("/leaderboard")
def leaderboard():
   selectedGame = request.args.get("game")
   leaderboardData = getLeaderboardFromGame(selectedGame)
   games = getAllGames()

   if not selectedGame or selectedGame == "all":
       selectedGame = None


   # Debug print to make sure it looks right
   #print("Games:", games)
   #print("Selected game:", selectedGame)
   #print("Leaderboard rows:", len(leaderboardData))
   return render_template(
       "leaderboard.html",
       leaderboard=leaderboardData,
       games=games,
       selected_game=selectedGame
   )


@app.route("/profile")
def profile():
    if "discordID" not in session:
        return redirect(url_for("discord.login"))


    user = {
        "id": session["discordID"],
        "name": session["username"],
        "avatar_url": session["avatarURL"]
    }

    personalLeaderboard = getPersonalLeaderboard(session["discordID"])
    scoresByGame = {}



    for row in personalLeaderboard:
        game = row["gameType"]

        if game not in scoresByGame:
            scoresByGame[game] = {
                "dates": [],
                "scores": []
            }


        scoresByGame[game]["dates"].append(
            row["timeSubmitted"][:10]  # YYYY-MM-DD
        )

        scoresByGame[game]["scores"].append(row["score"])

    return render_template(
        "profile.html",
        user=user,
        personalScores=personalLeaderboard,
        scoresByGame=scoresByGame
    )


@app.route("/submitScore", methods=["GET", "POST"])
def submitScore():
    if "discordID" not in session:
        return redirect(url_for("login"))

    isAdmin = checkAdmin(session["discordID"])

    if request.method == "POST":
        game = request.form.get("game")
        score = request.form.get("score", type=int)
        destination = request.form.get("destination", "personal")
        notes = request.form.get("notes") or ""

        date_achieved = request.form.get("date_achieved")
        if not date_achieved:
            date_achieved = None

        player_name = request.form.get("player_name") if isAdmin else session["username"]
        link = request.form.get("link") if isAdmin else ""

        # minimumScores is used to ensure that any score that does not meet the community
        # minimum cannot be uploaded to the leaderboard, making sure that any typos
        # don't cause problems
        minimumScores = {
            "Tetris.com": 1500000,
            "MindBender": 500000,
            "E60": 100000,
            "NBlox": 1000000
        }

        if not game or score is None:
            flash("Please fill in all required fields", "warning")
            return redirect(url_for("submitScore"))

        if isAdmin and destination == "official":

            if game in minimumScores and score < minimumScores[game]:
                flash(f"The score does not meet the minimum for {game}", "warning")
                return redirect(url_for("submitScore"))

            if not player_name or not link:
                flash("Admin submissions require a player name and a proof link", "warning")
                return redirect(url_for("submitScore"))

            submitOfficialLeaderboard(
                username=player_name,
                score=score,
                link=link,
                gameType=game,
                submittedBy=session["username"],
                notes=notes
            )

            flash("Score submitted to official leaderboard!", "success")
            return redirect(url_for("leaderboard"))

        # Personal scores (admins + normal users)

        submitPersonalScores(
            discordID=session["discordID"],
            score=score,
            gameType=game,
            notes=notes,
            date_achieved=date_achieved
        )

        flash("Score added to your personal profile!", "success")
        return redirect(url_for("profile"))

    return render_template("submit_score.html")


@app.route("/deleteScore", methods=["GET", "POST"])
def deleteScore():
    if "discordID" not in session or not checkAdmin(session["discordID"]):
        return redirect(url_for("login"))

    deleted = None

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        game = request.form.get("game", "").strip()
        scoreA = request.form.get("score", "").strip()

        if not username or not game or not scoreA:
            flash("Fill in all the fields", "warning")
        else:
            try:
                score = int(scoreA)
            except ValueError:
                flash("Score must be a number, and without commas", "warning")
            else:
                deleted = deleteExactScore(username=username, gameType=game, score=score)

                if deleted:
                    flash(f"Deleted {score} points for {username} in {game}", "success")
                else:
                    flash("That score couldn't be found. Nothing deleted", "success")

    return render_template("delete_score.html")

@app.route("/about")
def about():
   return render_template("about.html")


@app.route("/arbitraryClub")
def arbitraryClub():
    rawData = getBestScoresByPlayer()

    games = ["Tetris.com (Untuned)", "Tetris.com (Tuned)", "MindBender", "E60", "NBlox"]

    matrix = {}

    for row in rawData:

        player = row["username"]

        game = row["gameType"]

        score = row["bestScore"]

        tier = getArbitraryTiers(game, score)

        if player not in matrix:
            matrix[player] = {g: None for g in games}

        matrix[player][game] = tier

    return render_template(
        "arbitraryClub.html",
        matrix=matrix,
        games=games

    )



@app.route("/deletePersonalScore", methods=["POST"])
def deletePersonalScore():
    if "discordID" not in session:
        return redirect(url_for("login"))

    scoreID = request.form.get("scoreID")
    if not scoreID:
        flash("Invalid Request", "warning")
        return redirect(url_for("profile"))

    try:
        scoreID = int(scoreID)
    except ValueError:
        flash("Invalid Score ID", "warning")
        return redirect(url_for("profile"))

    deleted = deletePersonalScoreForUser(session["discordID"], scoreID)

    if deleted:
        flash("Score is deleted.", "success")
    else:
        flash("Score couldn't be found or was already deleted", "warning")

    return redirect(url_for("profile"))

@app.route("/downloadData")
def downloadData():
    if "discordID" not in session:
        return redirect(url_for("login"))
    # Gets all the information from the logged in user to ensure that only their data is being downloaded
    discord_id = session["discordID"]
    user = getUserByID(discord_id)
    scores = getPersonalLeaderboard(discord_id)

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["username", "game", "score", "date"])

    for score in scores:
        writer.writerow([
            score["gameType"],
            score["score"],
            score["timeSubmitted"]
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = (
        "attachment; filename=Personal Scores.csv"
    )

    return response


@app.route("/deleteAccount", methods=["POST"])
def deleteAccount():
    if "discordID" not in session:
        return redirect(url_for("login"))
    discordID = session["discordID"]
    permanentlyDeleteUser(discordID)
    session.clear()
    flash("Your personal data and account have been deleted")
    return redirect(url_for("home"))

# --- Login / Logout ---
@app.route("/login")
def login():
   return loginUser()

@app.route("/logout")
def logout():
   return logoutUser()


@app.route("/login/complete")
def loginComplete():
    return loginUser()



@app.route("/debug-session") # I had to add this because for TWO DAYS the login stuff would not work after I added the database and I didn't know why. Eventually I wanted to just figure out if I was remaining logged in, because my UI said I wasn't, and this showed me I was logged in because all my info was there... I don't understand why OAuth has to be so hard
def debug():
    return dict(session)

@app.route("/debug-database") # I made this to check if the database was actually working, which it is.
def debugDB():
    return getDebug()


# --- Run app ---
if __name__ == "__main__":
   app.run(debug=True)