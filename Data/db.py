import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def getConnection(): # This saves me from rewriting the line below for every time I want to open a new connection
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def createDB():
    conn = getConnection()
    command = conn.cursor()

    #Creates the table to store the user information from Discord.
    command.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discordID TEXT UNIQUE NOT NULL,
    username TEXT NOT NULL,
    avatarURL TEXT,
    isAdmin INTEGER DEFAULT 0
    )
    """)
    # The submittedBy field and timeSubmitted field is for the mod's name and current time as a way to hold them accountable
    # The gameType is to check which of the four games it is. Either Tetris.com, MindBender, E60 or N-blox

    #For the overall leaderboard that everyone will care about
    command.execute("""
    CREATE TABLE IF NOT EXISTS publicLeaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    score INTEGER NOT NULL,
    link TEXT NOT NULL,
    gameType TEXT,
    submittedBy TEXT NOT NULL,
    timeSubmitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
    )""")

    # For the private leaderboards to track scores
    command.execute("""
        CREATE TABLE IF NOT EXISTS personalLeaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discordID TEXT NOT NULL,
        score INTEGER NOT NULL,
        gameType TEXT NOT NULL,
        timeSubmitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT NOT NULL
        )""")

    conn.commit()
    conn.close()

def insert_user(discordID, username, avatarURL, isAdmin=0):
        conn = getConnection()
        command = conn.cursor()
        command.execute("""
        INSERT OR IGNORE INTO users(discordID, username, avatarURL, isAdmin)
        VALUES (?, ?, ?, ?)
        """, (discordID, username, avatarURL, isAdmin))

        conn.commit()
        conn.close()


def getUserByID(discordID):
    conn = getConnection()
    command = conn.cursor()
    command.execute(
        "SELECT * FROM users WHERE discordID = ?",
        (discordID, )
    )
    user = command.fetchone()
    conn.close()
    return user


def getLeaderboardFromGame(game=None):
   conn = getConnection()
   command = conn.cursor()
   if game:
       command.execute("""
       SELECT *
       FROM publicLeaderboard
       WHERE id IN (
           SELECT MAX(id)
           FROM publicLeaderboard
           WHERE gameType = ?
           GROUP BY username
       )
       ORDER BY score DESC
       """, (game,))
   else:
       command.execute("""
       SELECT *
       FROM publicLeaderboard
       WHERE id IN (
           SELECT MAX(id)
           FROM publicLeaderboard
           GROUP BY username, gameType
       )
       ORDER BY score DESC
       """)
   rows = command.fetchall()
   conn.close()
   return [dict(row) for row in rows]

def getAllUsers():
    conn = getConnection()
    command = conn.cursor()
    command.execute("SELECT username FROM users")
    rows = command.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def getAllGames():
   conn = getConnection()
   command = conn.cursor()
   command.execute("SELECT DISTINCT gameType FROM publicLeaderboard")
   rows = command.fetchall()
   conn.close()
   # Filter out None and sort nicely
   games = [row["gameType"] for row in rows if row["gameType"]]
   return games
def tempLeaderboardData():
# Placeholder leaderboard data
    leaderboard_data = [
       {"username": "Ace", "score": 3600000, "game": "Tetris.com"},
       {"username": "Denver", "score": 3300000, "game": "Tetris.com"}
   ]
    return leaderboard_data or []

def submitOfficialLeaderboard(username, score, link, gameType, submittedBy, notes=""):
    conn = getConnection()
    command = conn.cursor()
    command.execute(
        """INSERT INTO publicLeaderboard (
        username, 
        score, 
        link, 
        gameType, 
        submittedBy, 
        notes
        
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
            username,
            score,
            link,
            gameType,
            submittedBy,
            notes
        ))
    conn.commit()
    conn.close()

def deleteOfficialScore(username, gameType, score):
    conn = getConnection()
    command = conn.cursor()

    command.execute("""
    DELETE FROM officialLeaderboard
    WHERE username = ?
    AND gameType = ?
    AND score = ?
    """,
    (username, gameType, score)
    )

    rowsDeleted = command.rowcount
    conn.commit()
    conn.close()

    return rowsDeleted > 0

def getPersonalLeaderboard(discordID):
    conn = getConnection()
    command = conn.cursor()
    command.execute("""
    SELECT
    score,
    gameType
    FROM personalLeaderboard
    WHERE discordID = ?
    """, (discordID, ))

    rows = command.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def submitPersonalScores(discordID, score, gameType, notes):
    conn = getConnection()
    command = conn.cursor()
    command.execute("""
    INSERT INTO personalLeaderboard (
    discordID,
    score,
    gameType,
    notes
    )
    VALUES (?, ?, ?, ?)""",
    (discordID, score, gameType, notes)
    )
    conn.commit()
    conn.close()

def deleteExactScore(username, score, gameType):
    conn = getConnection()
    command = conn.cursor()
    command.execute("""DELETE FROM publicLeaderboard 
                    WHERE username = ?
                    AND score = ?
                    AND gameType = ?
                    """, (username, score, gameType))
    rowsDeleted = command.rowcount

    conn.commit()
    conn.close()

    return rowsDeleted > 0

def getDebug():
    conn = getConnection()
    command = conn.cursor()
    command.execute("SELECT discordID, username FROM users")
    users = command.fetchall()
    command.execute("SELECT * FROM publicLeaderboard")
    scores = command.fetchall()
    command.execute("SELECT * from personalLeaderboard")
    pLB = command.fetchall()

    conn.close()
    return {"users": [dict(u) for u in users],
            "publicLeaderboard": [dict(s) for s in scores],
            "personalLeaderboard": [dict(d) for d in pLB]}



if __name__ == "__main__":
    createDB()

    print("Database initialised")