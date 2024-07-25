import os
import requests
from dotenv import load_dotenv

load_dotenv()

USER_TOKEN = os.getenv('USER_TOKEN')


def api_call(method, params):
    response = requests.get(f'https://api.vk.com/method/{method}', params=params)
    return response.json()


def get_city_id(city_name, token):
    params = {
        'access_token': token,
        'v': '5.131',
        'q': city_name,
        'count': 1
    }
    response = api_call('database.getCities', params)
    if response['response']['items']:
        return response['response']['items'][0]['id']
    return None


def search_users(gender, age, city_id, token):
    params = {
        'access_token': token,
        'v': '5.131',
        'sex': gender,
        'age_from': age,
        'age_to': age,
        'city': city_id,
        'has_photo': 1,  # Только с фотографиями
        'fields': 'photo_max_orig,domain',
        'count': 1000
    }
    response = api_call('users.search', params)
    return response.get('response', {}).get('items', [])


def get_user_info(user_ids, token):
    params = {
        'access_token': token,
        'v': '5.131',
        'user_ids': ','.join(map(str, user_ids)),
        'fields': 'photo_max_orig,domain'
    }
    response = api_call('users.get', params)
    return response.get('response', [])


def get_top_photos(user_id, token, count=3):
    params = {
        'access_token': token,
        'v': '5.131',
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1,  # Получаем и лайки
        'photo_sizes': 1  # Получаем список размеров каждой фотографии
    }
    response = api_call('photos.get', params)
    if 'response' in response:
        photos = response['response']['items']
        photos.sort(key=lambda x: x['likes']['count'], reverse=True)
        top_photos = photos[:count]
        return [f'photo{user_id}_{photo["id"]}' for photo in top_photos]
    return []


def get_random_user(users):
    from random import choice
    return choice(users) if users else None
