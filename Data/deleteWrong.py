# This was made because I was testing the score submission and realised I didn't have an easy
# way to delete scores

from Data.db import getConnection

discordIDToDelete = "1367787837981851740"

conn = getConnection()
command = conn.cursor()

command.execute("DELETE FROM publicLeaderboard WHERE submittedBy = ?", (discordIDToDelete,))

conn.commit()
conn.close()

print("Deleted")