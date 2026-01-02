import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # For local tessting
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_dance.contrib.discord import make_discord_blueprint, discord
from dotenv import load_dotenv
from Data.db import createDB, getUserByID, insert_user, tempLeaderboardData, getDebug, submitOfficialLeaderboard, getLeaderboardFromGame, getAllGames  # My database helper functions
load_dotenv()
from Logic.auth import loginUser, logoutUser
from Logic.session import createUser
from Logic.isAdmin import ADMIN_IDS, checkAdmin



app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")  # Session encryption
# --- OAuth2 Setup ---
discord_bp = make_discord_blueprint(
   client_id=os.getenv("DISCORD_CLIENT_ID"),
   client_secret=os.getenv("DISCORD_CLIENT_SECRET"),
   scope="identify"
)


app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    )

app.register_blueprint(discord_bp, url_prefix="/login")

# Initialises the database
#createDB()
@app.context_processor
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
   # Grab the selected game from query params (from button clicks)
   selected_game = request.args.get("game")
   # Get the leaderboard data for that game (or all if None)
   leaderboard_data = getLeaderboardFromGame(selected_game)
   # Get all unique games for toggle buttons
   games = getAllGames()


   # Debug print to make sure it looks right
   print("Games:", games)
   print("Selected game:", selected_game)
   print("Leaderboard rows:", len(leaderboard_data))
   return render_template(
       "leaderboard.html",
       leaderboard=leaderboard_data,
       games=games,
       selected_game=selected_game
   )

@app.route("/profile")
def profile():
   # Only allow logged-in users
   if "discordID" not in session:
       return redirect(url_for("discord.login"))
   # Use session data to avoid repeated Discord API calls
   user = {
       "id": session["discordID"],
       "name": session["username"],
       "avatar_url": session["avatarURL"]
   }
   return render_template("profile.html", user=user)


@app.route("/submitScore", methods=["GET", "POST"])
def submitScore():
    if "discordID" not in session:
        return redirect(url_for("login"))

    isAdmin = checkAdmin(session["discordID"])

    if request.method == "POST":

        game = request.form.get("game")
        score = request.form.get("score", type=int)
        date_achieved = request.form.get("date_achieved")
        player_name = request.form.get("player_name") if isAdmin else session["username"]
        link = request.form.get("link") if isAdmin else ""
        notes = request.form.get("notes") or ""

        minimumScores = {

            "Tetris.com": 1_500_000,
            "MindBender": 500_000,
            "E60": 100_000,
            "NBlox": 1_000_000
        }

        # Admin submissions must meet minimum score

        if isAdmin and game in minimumScores and score < minimumScores[game]:
            flash(f"The score does not meet the minimum for {game}")

            return redirect(url_for("submitScore"))

        # Admin submissions require a player name and link

        if isAdmin and (not player_name or not link):
            flash("Admin submissions require a player name and a proof link")

            return redirect(url_for("submitScore"))

        # Submit the score

        submitOfficialLeaderboard(

            username=player_name,

            score=score,

            link=link,

            gameType=game,

            submittedBy=session["username"],

            notes=notes

        )

        flash("Score submitted successfully!")

        return redirect(url_for("leaderboard"))

    return render_template("submit_score.html")



@app.route("/about")
def about():
   return render_template("about.html")

# --- Login / Logout ---
@app.route("/login")
def login():
   return loginUser()

@app.route("/logout")
def logout():
   return logoutUser()

@app.route("/debug-session") # I had to add this because for TWO DAYS the login stuff would not work after I added the database and I didn't know why. Eventually I wanted to just figure out if I was remaining logged in, because my UI said I wasn't, and this showed me I was logged in because all my info was there... I don't understand why OAuth has to be so hard
def debug():
    return dict(session)

@app.route("/debug-database") # I made this to check if the database was actually working, which it is.
def debugDB():
    return getDebug()


# --- Run app ---
if __name__ == "__main__":
   app.run(debug=True)