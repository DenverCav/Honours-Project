import pandas as pd

from Data.db import getConnection

EXCELPATH = "DataForLBSetup.xlsx"


def importScores():
    # Read Excel

    df = pd.read_excel(EXCELPATH)

    conn = getConnection()

    command = conn.cursor()

    for _, row in df.iterrows():

        username = row["Name"]

        score = int(str(row["Score"]).replace(",", ""))  # Remove commas

        link = row["Link"]

        notes = row["Notes"]

        game_type = row["GameType"]

        tuning = row["Tuning"] if row["Tuning"] != "" else "Untuned"

        submittedBy = "Historical Leaderboard Data"

        # Only add tuning info for Tetris.com

        if game_type == "Tetris.com":
            game_type = f"Tetris.com ({tuning})"

        # Insert into database

        command.execute("""

            INSERT INTO publicLeaderboard 

            (username, score, link, gameType, submittedBy, notes)

            VALUES (?, ?, ?, ?, ?, ?)

        """, (

            username,

            score,

            link,

            game_type,

            submittedBy,

            notes

        ))

    conn.commit()

    conn.close()

    print("Imported the old data successfully!")


if __name__ == "__main__":
    importScores()
