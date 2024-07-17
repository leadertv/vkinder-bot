import sqlite3
from . import logging

DATABASE_FILE = "bot.db"

def connect_to_db():
    """Установка соединения с базой данных"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        return conn
    except sqlite3.Error as e:
        logging.error(f"Ошибка при подключении к базе данных: {e}")
        return None

def create_tables(conn):
    """Создание таблиц в базе данных, если они еще не существуют"""
    try:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            city TEXT,
            profile_url TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            file_name TEXT,
            file_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            photo_url TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при создании таблиц: {e}")

def save_user(conn, user_info):
    """Сохранение информации о пользователе в таблице users"""
    try:
        c = conn.cursor()
        c.execute("INSERT INTO users (first_name, last_name, age, city, profile_url) VALUES (?, ?, ?, ?, ?)", (
            user_info["first_name"],
            user_info["last_name"],
            user_info["age"],
            user_info["city"],
            user_info["profile_url"]
        ))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении пользователя: {e}")

def save_photo(conn, user_id, file_name, file_path):
    """Сохранение информации о фотографии пользователя в таблице photos"""
    try:
        c = conn.cursor()
        c.execute("INSERT INTO photos (user_id, file_name, file_path) VALUES (?, ?, ?)", (user_id, file_name, file_path))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении фотографии: {e}")

def get_favorite_photos(conn, user_id, page=1, per_page=10):
    """Получение списка избранных фотографий пользователя с учетом пагинации"""
    try:
        c = conn.cursor()
        offset = (page - 1) * per_page
        c.execute("SELECT photo_url FROM favorites WHERE user_id = ? LIMIT ? OFFSET ?", (user_id, per_page, offset))
        return [row[0] for row in c.fetchall()]
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении избранных фотографий: {e}")
        return []

def add_to_favorites(conn, user_id, photo_url):
    """Добавление фотографии в список избранных для пользователя"""
    try:
        c = conn.cursor()
        c.execute("INSERT INTO favorites (user_id, photo_url) VALUES (?, ?)", (user_id, photo_url))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при добавлении фотографии в избранное: {e}")

def remove_from_favorites(conn, user_id, photo_url):
    """Удаление фотографии из списка избранных для пользователя"""
    try:
        c = conn.cursor()
        c.execute("DELETE FROM favorites WHERE user_id = ? AND photo_url = ?", (user_id, photo_url))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при удалении фотографии из избранного: {e}")