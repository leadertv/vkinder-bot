import os
import logging
from vk_api.longpoll import VkLongPoll, VkEventType
from vk.vk_api import handle_message
from db.db_helper import connect_to_db, create_tables

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    # Подключение к базе данных и создание таблиц
    conn = connect_to_db()
    if conn:
        create_tables(conn)

    # Подключение к VK API
    vk_api = connect_to_vk()
    if vk_api:
        # Инициализация LongPoll
        longpoll = VkLongPoll(vk_api)

        # Обработка входящих сообщений
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                response = handle_message(event)
                if response:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message=response
                    )

if __name__ == "__main__":
    main()