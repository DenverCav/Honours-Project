import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

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

@app.context_processor
def createUser():
    if discord.authorized:
        resp = discord.get("/api/users/@me")
        if resp.ok:
            user = resp.json()
            return {
                "logged_in": True,
                "user_pfp": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png",
                "username": user["username"]
            }
        return {"logged_in": False}
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




@app.route("/add_score")
def add_score_route():
   # Placeholder: show form for adding personal scores
   return render_template("add_score.html")
@app.route("/admin_add_score")
def admin_add_score_route():
   # Placeholder: show form for admins to add official scores
   return render_template("admin_add_score.html")
# Optional: simple test page
@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")


# ---------- RUN APP ----------
if __name__ == "__main__":
   app.run(debug=True)