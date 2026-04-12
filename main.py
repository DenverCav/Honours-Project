import os, csv, uuid, secrets, html, time
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # For local tessting
from flask import Flask, render_template, redirect, url_for, session, request, flash, make_response
from flask_dance.contrib.discord import make_discord_blueprint, discord
from dotenv import load_dotenv
from io import StringIO
from urllib.parse import urlparse
from Data.db import createDB, getUserByID, insert_user, getDebug, submitOfficialLeaderboard, getLeaderboardFromGame, getAllGames, getPersonalLeaderboard, submitPersonalScores, getAllUsers, deleteExactScore, getUserScoreTimeline, deletePersonalScoreForUser, permanentlyDeleteUser, markUserForDeletion, getBestScoresByPlayer # My database helper functions
load_dotenv()
from Logic.auth import loginUser, logoutUser
from Logic.session import createUser
from Logic.isAdmin import ADMIN_IDS, checkAdmin
from Logic.arbitraryClub import getArbitraryTiers, normaliseGame
from Logic.profileLogic import getProfileData
from Logic.score import processScoreDeletion, processScoreSubmission, processPersonalScoreDeletion
from Logic.security import validateCSRF, isValidUrl
from Logic.downloadUserData import getUserPersonalScoresAsCSV


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
   if "csrfToken"  not in session:
       session["csrfToken"] = secrets.token_hex(32)

   if "discordID" in session:
       return {
           "logged_in": True,
           "username": session.get("username"),
           "user_pfp": session.get("avatarURL"),
           "is_admin": checkAdmin(session["discordID"]),
           "csrfToken": session["csrfToken"]
       }
   return {
       "logged_in": False,
       "username": None,
       "user_pfp": None,
       "is_admin": False,
       "csrfToken": session["csrfToken"]
   }



# --- Routes ---
@app.route("/")
def home():
   return render_template("home.html")


@app.route("/leaderboard")
def leaderboard():
   selectedGame = request.args.get("game")

   if selectedGame == "combined":
       leaderboardData = getLeaderboardFromGame("combined")
   else:
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

    personalScores, scoresByGame = getProfileData(session["discordID"])

    return render_template(
        "profile.html",
        user=user,
        personalScores=personalScores,
        scoresByGame=scoresByGame
    )


@app.route("/submitScore", methods=["GET", "POST"])
def submitScore():
    if "discordID" not in session:
        return redirect(url_for("login"))

    isAdmin = checkAdmin(session["discordID"])

    if request.method == "POST":
        if not validateCSRF():
            return "CSRF validation failed", 403
        game = request.form.get("game")
        score = request.form.get("score", type=int)
        destination = request.form.get("destination", "personal")
        notes = html.escape(request.form.get("notes") or "")
        date_achieved = request.form.get("date_achieved") or None
        player_name = (
            html.escape(request.form.get("player_name"))
            if isAdmin else session["username"]
        )
        link = request.form.get("link") if isAdmin else ""

        status, message, redirectPage = processScoreSubmission(
            session["discordID"],
            session["username"],
            isAdmin,
            game,
            score,
            destination,
            notes,
            date_achieved,
            player_name,
            link
        )

        flash(message, status)

        return redirect(url_for(redirectPage))

    return render_template("submit_score.html")


@app.route("/deleteScore", methods=["GET", "POST"])
def deleteScore():
    if "discordID" not in session or not checkAdmin(session["discordID"]):
        return redirect(url_for("login"))

    deleted = None

    if request.method == "POST":
        if not validateCSRF():
            return "CSRF validation failed", 403
        username = request.form.get("username", "").strip()
        game = request.form.get("game", "").strip()
        scoreA = request.form.get("score", "").strip()
        if not username or not game or not scoreA:
            flash("Fill in all the fields", "warning")
        else:
            try:
                score = int(scoreA)
            except ValueError:
                flash("Score must be a number", "warning")
            else:
                deleted = processScoreDeletion(username, game, score)
                if deleted:
                    flash(f"Deleted {score} points for {username} in {game}", "success")
                else:
                    flash("That score couldn't be found.", "warning")

    return render_template("delete_score.html")


@app.route("/demo")
def demo():
    demoID = f"demo{uuid.uuid4().hex[:8]}"

    session["discordID"] = demoID
    session["username"] = f"DemoUser{demoID[-4:]}"
    session["avatarURL"] = "/static/images/Null.png"
    session["isDemo"] = True

    session["demoCreatedAt"] = time.time()

    return redirect(url_for("home"))


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
    if not validateCSRF():
        return "CSRF validation failed", 403
    scoreID = request.form.get("scoreID")
    try:
        scoreID = int(scoreID)
    except:
        flash("Invalid Score ID", "warning")
        return redirect(url_for("profile"))

    deleted = processPersonalScoreDeletion(session["discordID"], scoreID)
    if deleted:
        flash("Score is deleted.", "success")
    else:
        flash("Score couldn't be found.", "warning")
    return redirect(url_for("profile"))


@app.route("/downloadData")
def downloadData():
    if "discordID" not in session:
        return redirect(url_for("login"))

    csvData = getUserPersonalScoresAsCSV(session["discordID"])

    response = make_response(csvData)

    response.headers["Content-Type"] = "text/csv"

    response.headers["Content-Disposition"] = "attachment; filename=Personal Scores.csv"

    return response


@app.route("/deleteAccount", methods=["POST"])
def deleteAccount():
    if "discordID" not in session:
        return redirect(url_for("login"))
    if not validateCSRF():
        return "CSRF validation failed", 403
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
def loginComplete(): # This part originally just returned the loginUser() function, but one of my users said that there was a infinite redirect loop when clicking cancel on Discord OAuth, which this new code now fixes
    success = loginUser()

    if not success:
        session["loginFailed"] = True
        flash("Login cancelled.", "warning")
        return redirect(url_for("home"))

    session.pop("loginFailed", None)
    return redirect(url_for("home"))


@app.before_request
def checkDemoExpiry():
    if session.get("isDemo"):
        created = session.get("demoCreatedAt")

        if created:
            if time.time() - created > 600: # 10 minutes
                session.clear()
                flash("Demo session expired, please start again.", "warning")
                return redirect(url_for("home"))

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self';"
        "img-src 'self' https://cdn.discordapp.com;"
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline';"
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline';"
    )

    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.route("/debug-session") # I had to add this because for TWO DAYS the login stuff would not work after I added the database and I didn't know why. Eventually I wanted to just figure out if I was remaining logged in, because my UI said I wasn't, and this showed me I was logged in because all my info was there... I don't understand why OAuth has to be so hard
def debug():
    return dict(session)

@app.route("/debug-database") # I made this to check if the database was actually working, which it is.
def debugDB():
    return getDebug()


# --- Run app ---
if __name__ == "__main__":
   app.run(debug=True)