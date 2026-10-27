import bcrypt
import sqlite3

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Retrieve user data based on username or email
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
    user = cursor.fetchone()

    conn.close()

    if user:  # If the user is found
        stored_password = user[2]  # The stored hashed password

        # Check if the input password matches the stored hashed password
        if bcrypt.checkpw(password.encode(), stored_password.encode()):
            return True  # Password matches
        else:
            return False  # Incorrect password
    else:
        return False  # User does not exist
