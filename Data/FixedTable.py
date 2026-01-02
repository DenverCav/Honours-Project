from db import getConnection
def createDB():
    conn = getConnection()
    command = conn.cursor()

    command.execute("DROP table publicLeaderboard")

    command.execute("""
    CREATE TABLE IF NOT EXISTS publicLeaderboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    score INTEGER NOT NULL,
    link TEXT NOT NULL,
    gameType TEXT,
    submittedBy TEXT,
    timeSubmitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
    )""")

    conn.commit()
    conn.close()
    print("Table remade")

if __name__ == "__main__":
    createDB()
