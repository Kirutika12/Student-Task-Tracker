
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing. Check your .env file.")

    connection = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )

    return connection


def create_table():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id BIGSERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                completed INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'Medium',
                user_id BIGINT REFERENCES users(id)
            )
        """)

        connection.execute("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'Medium'
        """)

        connection.execute("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS user_id BIGINT REFERENCES users(id)
        """)

        connection.commit()

    finally:
        connection.close()
