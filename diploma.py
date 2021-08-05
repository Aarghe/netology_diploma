import time
import threading
import requests
from pprint import pprint
from datetime import datetime


class YaUploader:
    def __init__(self, token, dict_files):
        self.token = token
        self.dict_files = dict_files

    def get_headers(self, token):
        return {'Content-Type': 'application/json',
                'Authorization': token
                }

    def get_params(self, url, path):
        return {'path': path,
                'overwrite': 'true',
                'url': url
                }

    def upload_files(self):
        link = r'https://cloud-api.yandex.net/v1/disk/resources/upload'
        today = datetime.today().date()
        requests.put(r'https://cloud-api.yandex.net/v1/disk/resources',
                     params=self.get_params('', today),
                     headers=self.get_headers(self.token))
        result_json = {}
        with open('log.txt', 'a', encoding='utf-8') as logfile:
            print('', file=logfile)
            print(f'{time.ctime()} начинается загрузка фотографий на YaDisk', file=logfile)
            print(f'файлов к загрузке: {len(self.dict_files)}', file=logfile)

        for file in self.dict_files:
            url = self.dict_files[file]
            headers = self.get_headers(self.token)
            params = self.get_params(url, str(today) + '/' + file)
            request = requests.post(link, headers=headers, params=params)
            response = request.json()
            result_json[url] = [request.status_code, file]
            with open('log.txt', 'a', encoding='utf-8') as logfile:
                if request.status_code == 202:
                    print(f'фото загружно; лайки: {str(file)}; ссылка VK: {url}', file=logfile)
                else:
                    print(f'фото не загружно; лайки: {str(file)}; ссылка VK: {url}', file=logfile)
        return result_json


class VkPhotos:
    def __init__(self, id, vk_token, quantity_to_upload=5):
        self.id = id
        self.quantity_to_upload = quantity_to_upload
        self.vk_token = vk_token

    def get_params(self, token):
        return {'owner_id': self.id,
                'album_id': 'profile',
                'extended': 1,
                'photo_sizes': 1,
                'count': 1000,
                'v': '5.131',
                'access_token': token
                }

    def get_photos(self):
        link = 'https://api.vk.com/method/photos.get'
        token = self.vk_token
        params = self.get_params(token)
        response = requests.get(link, params=params)
        response_json = response.json()['response']['items']
        sizes_dict = {}
        for item in response_json:
            current_max = 0
            for photo in item['sizes']:
                if photo['height'] != 0:
                    photo_size = photo['width'] * photo['height']
                else:
                    photo_size = 0
                if photo_size >= current_max:
                    sizes_dict[item['id']] = [photo_size, item['likes']['count'], photo['url']]
        sorted_sizes = sorted(sizes_dict.values(), reverse=True)
        if len(sorted_sizes) < self.quantity_to_upload:
            self.quantity_to_upload = len(sorted_sizes)
        photos_for_upload = {}
        for i in range(self.quantity_to_upload):
            sorted_sizes[i][1] = str(sorted_sizes[i][1])
            if sorted_sizes[i][1] in photos_for_upload:
                sorted_sizes[i][1] += '_'
            photos_for_upload[sorted_sizes[i][1]] = sorted_sizes[i][2]
        pprint(photos_for_upload)
        return photos_for_upload


vk_token = ''
a = VkPhotos('1', vk_token)

ya_token = ''
b = YaUploader(ya_token, a.get_photos())
b.upload_files()
