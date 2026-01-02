import sqlite3, os
from Data.db import getConnection

DB_PATH = os.path.join("Data", "database.db")
conn = getConnection()
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT DISTINCT gameType FROM publicLeaderboard")
rows = c.fetchall()
for row in rows:
    print(row["gameType"])

conn.close()