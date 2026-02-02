from flask import session, redirect, url_for
from flask_dance.contrib.discord import discord
from Data.db import getUserByID, insert_user

def loginUser():
    if not discord.authorized:
        return redirect(url_for("discord.login"))
    resp = discord.get("/api/users/@me")
    if not resp.ok:
        # Something went wrong with the Discord API
        return redirect(url_for("home"))
    user_info = resp.json()
    # Save user info in session
    session["discordID"] = user_info["id"]
    session["username"] = user_info["username"]
    session["avatarURL"] = f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png"

    session.modified = True;
    # Insert into database if new
    if not getUserByID(user_info["id"]):
        insert_user(user_info["id"], user_info["username"], session["avatarURL"])
    return redirect(url_for("home"))

def logoutUser():
    session.clear()
    return redirect(url_for("home"))