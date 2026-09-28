import sqlite3

DB_PATH = "database/znu_food.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            auto_reservation INTEGER DEFAULT 1
        )
    """)

    connection.commit()
    connection.close()


def save_user(telegram_id, username, password):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (telegram_id, username, password)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id)
        DO UPDATE SET
            username = excluded.username,
            password = excluded.password
    """, (telegram_id, username, password))

    connection.commit()
    connection.close()


def get_user(telegram_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT telegram_id, username, password, auto_reservation
        FROM users
        WHERE telegram_id = ?
    """, (telegram_id,))

    user = cursor.fetchone()

    connection.close()

    return user
