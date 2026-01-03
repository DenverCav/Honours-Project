import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # For local tessting
from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_dance.contrib.discord import make_discord_blueprint, discord
from dotenv import load_dotenv
from Data.db import createDB, getUserByID, insert_user, tempLeaderboardData, getDebug, submitOfficialLeaderboard, getLeaderboardFromGame, getAllGames, getPersonalLeaderboard, submitPersonalScores # My database helper functions
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
   selectedGame = request.args.get("game")
   leaderboardData = getLeaderboardFromGame(selectedGame)
   games = getAllGames()


   # Debug print to make sure it looks right
   print("Games:", games)
   print("Selected game:", selectedGame)
   print("Leaderboard rows:", len(leaderboardData))
   return render_template(
       "leaderboard.html",
       leaderboard=leaderboardData,
       games=games,
       selected_game=selectedGame
   )

@app.route("/profile")
def profile():
   # Only allow logged-in users
   if "discordID" not in session:
       return redirect(url_for("discord.login"))
   user = {
       "id": session["discordID"],
       "name": session["username"],
       "avatar_url": session["avatarURL"]
   }

   personalScores = getPersonalLeaderboard(session["discordID"])

   return render_template("profile.html", user=user, personalScores=personalScores)


@app.route ("/submitScore", methods=["GET", "POST"])
def submitScore():
    if "discordID" not in session:
        return redirect(url_for("discord.login"))

    is_admin = checkAdmin(session["discordID"])

    if request.method == "POST":
        game = request.form["game"]
        score = int(request.form["score"])
        notes = request.form.get("notes", "")

        # Admins choose destination

        if is_admin:
            destination = request.form.get("destination", "official")

            if destination == "official":
                link = request.form["link"]
                player_name = request.form["player_name"]

                submitOfficialLeaderboard(
                    username=player_name,
                    score=score,
                    link=link,
                    gameType=game,
                    submittedBy=session["username"],
                    notes=notes

                )

            else:  # personal

                submitPersonalScores(
                    discordID=session["discordID"],
                    score=score,
                    gameType=game,
                    notes=notes

                )

        # Non-admins always submit personal

        else:

            submitPersonalScores(
                discordID=session["discordID"],
                score=score,
                gameType=game,
                notes=notes

            )
        flash("Score submitted successfully!")
        return redirect(url_for("profile"))

    return render_template(
        "submit_score.html",
        is_admin=is_admin

    );



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