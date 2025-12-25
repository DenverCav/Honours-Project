import os
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_dance.contrib.discord import make_discord_blueprint, discord

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

#OAuth2 Setup here
discord_bp = make_discord_blueprint(
    client_id=os.getenv("DISCORD_CLIENT_ID"),
    client_secret=os.getenv("DISCORD_CLIENT_SECRET"),
    scope="identify"
)
app.register_blueprint(discord_bp, url_prefix="/login")
#One night the context_processor just stopped working and I don't know why, I shouldn't have to know why
#and I shouldn't need tp wonder why. Gut it got fixed...

@app.context_processor
def createUser():
    if discord.authorized:
        resp = discord.get("/api/users/@me")
        if resp.ok:
            user = resp.json() # To save this to the database later (tm)
            return {
                "logged_in": True,
                "user_pfp": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png",
                "username": user["username"],
                "is_admin": False # To fix a bug right now
            }
    return {"logged_in": False, "user_pfp": None, "username": None}

#Routes between pages here

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/leaderboard")
def leaderboard():
    #Placeholder stuff here:
    leaderboard_data = [ {"username": "Ace", "score": 3600000, "game": "Tetris.com"},
                         {"username": "Denver", "score": 3300000, "game": "Tetris.com"}]
    return render_template("leaderboard.html", leaderboard=leaderboard_data)

@app.route("/profile")
def profile():
   if not discord.authorized:
       return redirect(url_for("discord.login"))

   resp = discord.get("/api/users/@me")
   user_info = resp.json()

   return render_template("profile.html", user={
                          "name": user_info["username"],
                           "id": user_info["id"],
                          "avatar_url": f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"
                         })
@app.route("/submitScore")
def submitScore():
    return render_template("submit_score.html")





@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/logout")
def logout():
    token = discord_bp.token
    if token:
        del discord_bp.token
    session.clear()
    return render_template("home.html")

@app.route("/login") # Everything breaks if I get rid of this
def login():
    if not discord.authorized:
        return redirect(url_for("discord.login"))

    resp = discord.get("/api/users/@me")
    user_info = resp.json()
    return render_template("home.html")


# ---------- RUN APP ----------
if __name__ == "__main__":
   app.run(debug=True)