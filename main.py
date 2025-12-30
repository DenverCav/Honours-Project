import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # For local tessting
from flask import Flask, render_template, redirect, url_for, session
from flask_dance.contrib.discord import make_discord_blueprint, discord
from dotenv import load_dotenv
from Data.db import createDB, getUserByID, insert_user, tempLeaderboardData, getDebugUsers  # My database helper functions
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
    leaderboard_data = tempLeaderboardData()
    return render_template("leaderboard.html", leaderboard=leaderboard_data or [])

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


@app.route("/submitScore")
def submitScore():
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
    return getDebugUsers()


# --- Run app ---
if __name__ == "__main__":
   app.run(debug=True)