import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Delete all users (WARNING: this clears your table)
cursor.execute("DELETE FROM users")

conn.commit()
conn.close()

print("All users deleted.")
