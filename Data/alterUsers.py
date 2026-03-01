import sqlite3
from db import getConnection

DB_PATH = "Data/database.db"  # change if needed

def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return column in [row[1] for row in cursor.fetchall()]

def alterUsers():
    conn = getConnection()
    cur = conn.cursor()

    if not column_exists(cur, "users", "isDeleted"):
        cur.execute("""
            ALTER TABLE users
            ADD COLUMN isDeleted INTEGER DEFAULT 0
        """)

        print("Added is_deleted column")

    if not column_exists(cur, "users", "deletionRequestedAt"):
        cur.execute("""
            ALTER TABLE users
            ADD COLUMN deletionRequestedAt TEXT
        """)

        print("Added deletion_requested_at column")

    conn.commit()
    conn.close()

    print("Migration complete.")

if __name__ == "__main__":
    alterUsers()
