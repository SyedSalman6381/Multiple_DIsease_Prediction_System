import bcrypt
import sqlite3

def register_user(username, email, password):
    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Check if the username or email already exists
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email))
    user = cursor.fetchone()

    if user:
        conn.close()
        return False  # Username or email already exists
    
    # Insert new user into the database with the hashed password
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                   (username, email, hashed_password))
    conn.commit()
    conn.close()
    return True
