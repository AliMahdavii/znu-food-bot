import sqlite3
from database.crypto import decrypt_password, encrypt_password


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
            auto_reservation INTEGER DEFAULT 1,
            reservation_days TEXT DEFAULT 'شنبه,یکشنبه,دوشنبه,سه‌شنبه,چهارشنبه',
            meal TEXT DEFAULT 'ناهار',
            selection_mode TEXT DEFAULT 'اولین غذای موجود'
        )
    """)

    connection.commit()
    connection.close()


def save_user(telegram_id, username, password):
    encrypted_password = encrypt_password(password)

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (telegram_id, username, password)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id)
            DO UPDATE SET
                username = excluded.username,
                password = excluded.password
        """, (telegram_id, username, encrypted_password))

        connection.commit()

    finally:
        connection.close()


def get_user(telegram_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                telegram_id,
                username,
                password,
                auto_reservation,
                reservation_days,
                meal,
                selection_mode
            FROM users
            WHERE telegram_id = ?
        """, (telegram_id,))

        user = cursor.fetchone()

        if user is None:
            return None

        user = list(user)
        user[2] = decrypt_password(user[2])

        return tuple(user)

    finally:
        connection.close()


def update_user_setting(telegram_id, field, value):
    allowed_fields = {
        "auto_reservation",
        "reservation_days",
        "meal",
        "selection_mode",
    }

    if field not in allowed_fields:
        raise ValueError("Invalid setting field.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        f"""
        UPDATE users
        SET {field} = ?
        WHERE telegram_id = ?
        """,
        (value, telegram_id)
    )

    connection.commit()
    connection.close()
