from db import getConnection

def checkDB():
    conn = getConnection()
    command = conn.cursor()
    command.execute("""
    UPDATE publicLeaderboard
    SET gameType = ?
    WHERE gameType IS NULL""", ("Tetris.com (Untuned)",))
    conn.commit()
    conn.close()
    print("Updated leaderboard")


if __name__ == "__main__":
    checkDB()

