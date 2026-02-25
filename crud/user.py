import sqlite3
from typing import Optional

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

def create_user(conn: sqlite3.Connection, username: str, password: str) -> dict:
    # hash password, insert into user table, return new user
    password_hash = pwd_context.hash(password)
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?) RETURNING id",
        (username, password_hash)
    )
    user_id = cursor.fetchone()["id"]
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    return user


def get_user_by_username(conn: sqlite3.Connection, username: str) -> dict | None:
    # find user by username, return eveyrthing associated or None if not found
    user = conn.execute("SELECT * FROM users WHERE username = ? ", (username,)).fetchone()
    return user