import os
import json
import vk_api
import time
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk.vk_api_helper import get_user_info, search_users, get_city_id, get_top_photos, get_random_user
from db.db_helper import init_db, add_to_favorites, remove_from_favorites, get_favorites_list
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
USER_TOKEN = os.getenv('USER_TOKEN')
GROUP_ID = int(os.getenv('GROUP_ID'))

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, GROUP_ID)

user_search_params = {}


def send_message(user_id, message, keyboard=None, attachment=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=int(time.time() * 1e6),
        keyboard=keyboard,
        attachment=attachment
    )


def create_keyboard(buttons):
    keyboard = VkKeyboard(one_time=False)
    for row in buttons:
        for idx, button in enumerate(row):
            if idx > 0:
                keyboard.add_line()
            keyboard.add_button(button['label'], color=VkKeyboardColor.PRIMARY if button[
                                                                                      'color'] == 'primary' else VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def main():
    while True:
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    user_id = event.obj.message['from_id']
                    text = event.obj.message['text'].lower()

                    if text == 'начать':
                        user_search_params[user_id] = {}
                        main_menu(user_id)
                    elif text == 'назад':
                        main_menu(user_id)
                    elif text == 'поиск':
                        user_search_params[user_id] = {}
                        search_menu(user_id)
                    elif text in ['мужчину', 'женщину', 'любой']:
                        set_gender(user_id, text)
                    elif 'gender' in user_search_params.get(user_id, {}) and (
                            'age' not in user_search_params[user_id] or user_search_params[user_id]['age'] == 'input'):
                        set_age(user_id, text)
                    elif 'age' in user_search_params.get(user_id, {}) and (
                            'city' not in user_search_params[user_id] or user_search_params[user_id][
                        'city'] == 'input'):
                        set_city(user_id, text)
                    elif text == 'следующий':
                        show_search_results(user_id)
                    elif text == 'в избранное':
                        add_to_favorites_handler(user_id)
                    elif text == 'избранные':
                        show_favorites(user_id)
                    elif text == 'начать заново':
                        user_search_params[user_id] = {}
                        main_menu(user_id)
                    else:
                        send_message(user_id, "Неизвестная команда. Попробуйте снова.")
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)


# Главное меню
def main_menu(user_id):
    buttons = [
        [{"label": "Поиск", "color": "primary"}],
        [{"label": "Избранные", "color": "primary"}],
        [{"label": "Начать заново", "color": "negative"}],
    ]
    keyboard = create_keyboard(buttons)
    send_message(user_id, "Добро пожаловать в VKinder! Выберите действие:", keyboard=keyboard)


# Меню выбора пола
def search_menu(user_id):
    buttons = [
        [{"label": "Мужчину", "color": "primary"}],
        [{"label": "Женщину", "color": "primary"}],
        # [{"label": "Любой", "color": "primary"}], Здесь надо будет работать с рандомом, не умею.
        [{"label": "Назад", "color": "negative"}],
    ]
    keyboard = create_keyboard(buttons)
    send_message(user_id, "Выберите пол, кого вы хотите найти:", keyboard=keyboard)


# Установка пола для поиска
def set_gender(user_id, text):
    if text == 'мужчину':
        gender = 2
    elif text == 'женщину':
        gender = 1
    else:
        gender = 0
    user_search_params[user_id]['gender'] = gender
    send_message(user_id, "Введите возраст и нажмите Enter:")
    user_search_params[user_id]['age'] = 'input'


# Установка возраста для поиска
def set_age(user_id, text):
    if text.isdigit() or text.lower() == 'любой':
        age = int(text) if text.isdigit() else 0
        user_search_params[user_id]['age'] = age
        send_message(user_id, "Введите город, например Иркутск:")
        user_search_params[user_id]['city'] = 'input'
    else:
        send_message(user_id, "Введите корректный возраст:")


# Установка города для поиска
def set_city(user_id, text):
    if text.lower() == 'любой':  # С любым как-то всё плохо работает. Не знаю как сделать.
        city_id = 1  # Предположим Москва по умолчанию
    else:
        city_id = get_city_id(text, USER_TOKEN)
        if not city_id:
            send_message(user_id, "Не удалось найти город. Попробуйте снова:")
            return

    user_search_params[user_id]['city'] = city_id
    show_search_results(user_id)


# Функция для показа результатов поиска
def show_search_results(user_id):
    params = user_search_params.get(user_id, {})
    gender = params.get('gender', 0)
    age = params.get('age', 0)
    city_id = params.get('city', 1)  # По умолчанию Москва

    users = search_users(gender, age, city_id, USER_TOKEN)
    if not users:
        send_message(user_id, "Ничего не найдено. Попробуйте снова.")
        return

    user = get_random_user(users)
    if not user:
        send_message(user_id, "Не удалось выбрать пользователя. Попробуйте снова.")
        return

    user_info = get_user_info([user['id']], USER_TOKEN)[0]
    attachment = ','.join(get_top_photos(user['id'], USER_TOKEN, count=3))
    profile_url = f"https://vk.com/{user_info['domain']}"

    message = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}\n{profile_url}"

    buttons = [
        [{"label": "Следующий", "color": "primary"}],
        [{"label": "В избранное", "color": "positive"}],
        [{"label": "Назад", "color": "negative"}]
    ]
    keyboard = create_keyboard(buttons)

    send_message(user_id, message, keyboard=keyboard, attachment=attachment)
    params['last_viewed'] = user


# Добавление в избранное
def add_to_favorites_handler(user_id):
    params = user_search_params.get(user_id, {})
    last_viewed = params.get('last_viewed')
    if not last_viewed:
        send_message(user_id, "Нет пользователя для добавления в избранное.")
        return

    user_info = get_user_info([last_viewed['id']], USER_TOKEN)[0]
    profile_url = f"https://vk.com/{user_info['domain']}"

    add_to_favorites(user_id, last_viewed['id'], user_info['first_name'], user_info['last_name'], profile_url)
    send_message(user_id, "Пользователь добавлен в избранное.")


# Показ избранных
def show_favorites(user_id):
    favorites_list = get_favorites_list(user_id)
    if not favorites_list:
        send_message(user_id, "У вас нет избранных пользователей.")
        return

    message = "Избранные пользователи:\n"
    for favorite in favorites_list:
        message += f"{favorite[1]} {favorite[2]} - {favorite[3]}\n"

    send_message(user_id, message)


# Удаление из избранного
def remove_from_favorites_handler(user_id, profile_url):
    user_id_to_remove = profile_url.split('/')[-1]
    user_info = get_user_info([user_id_to_remove], USER_TOKEN)[0]

    remove_from_favorites(user_id, user_info['id'])
    send_message(user_id, "Пользователь удален из избранного.")


if __name__ == "__main__":
    init_db()  # Инициализация базы данных
    main()
