import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute(
    "ALTER TABLE requests ADD COLUMN request_type TEXT"
)

conn.commit()
conn.close()

print("column added")