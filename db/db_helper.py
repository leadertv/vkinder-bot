import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv('DB_URL')


def get_connection():
    return psycopg2.connect(DB_URL)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            favorite_user_id BIGINT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            profile_url TEXT NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def add_to_favorites(user_id, favorite_user_id, first_name, last_name, profile_url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO favorites (user_id, favorite_user_id, first_name, last_name, profile_url)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, favorite_user_id, first_name, last_name, profile_url))

    conn.commit()
    cursor.close()
    conn.close()


def remove_from_favorites(user_id, favorite_user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM favorites WHERE user_id = %s AND favorite_user_id = %s
    """, (user_id, favorite_user_id))

    conn.commit()
    cursor.close()
    conn.close()


def get_favorites_list(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT favorite_user_id, first_name, last_name, profile_url FROM favorites WHERE user_id = %s
    """, (user_id,))

    favorites = cursor.fetchall()
    conn.close()

    return favorites
