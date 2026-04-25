# database.py - Database Setup
# This file creates the database and tables when the app starts

import sqlite3

# Name of our database file
DATABASE = "tasks.db"


def get_db_connection():
    """Connect to the SQLite database and return the connection"""
    conn = sqlite3.connect(DATABASE)
    # This lets us access columns by name (like a dictionary)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the database tables if they don't exist yet"""
    conn = get_db_connection()

    # Create the users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    # Create the tasks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()
