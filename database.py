import sqlite3
import json
from datetime import datetime

DATABASE_NAME = "pocketsmart.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_users_table():
    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            type TEXT NOT NULL,
            details TEXT,
            recommendation TEXT,
            created_at TEXT
        )
    """)

    # Add created_at to an older database if it does not already exist
    cursor.execute("PRAGMA table_info(history)")
    columns = [column[1] for column in cursor.fetchall()]

    if "created_at" not in columns:
        cursor.execute(
            "ALTER TABLE history ADD COLUMN created_at TEXT"
        )

    connection.commit()
    connection.close()


def create_user(name, email, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users (name, email, password)
        VALUES (?, ?, ?)
        """,
        (name, email, password)
    )

    connection.commit()
    connection.close()


def get_user(email, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name, email, password
        FROM users
        WHERE email = ? AND password = ?
        """,
        (email, password)
    )

    user = cursor.fetchone()
    connection.close()

    if user:
        return {
            "name": user[0],
            "email": user[1],
            "password": user[2]
        }

    return None


def save_history(email, history_type, details, recommendation):
    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO history
        (email, type, details, recommendation, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            email,
            history_type,
            json.dumps(details),
            json.dumps(recommendation),
            created_at
        )
    )

    connection.commit()
    connection.close()


def get_history(email):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT type, details, recommendation, created_at
        FROM history
        WHERE email = ?
        ORDER BY id DESC
        """,
        (email,)
    )

    rows = cursor.fetchall()
    connection.close()

    history = []

    for row in rows:
        history.append({
            "type": row[0],
            "details": json.loads(row[1]) if row[1] else {},
            "recommendation": json.loads(row[2]) if row[2] else {},
            "created_at": row[3]
        })

    return history