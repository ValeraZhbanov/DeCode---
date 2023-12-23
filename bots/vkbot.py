# -*- coding: cp1251 -*-

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id


class VkBot:

    def __init__(self, token):

        # Объект для выполнения запросов к вк
        self.vk = vk_api.VkApi(token=token)

        # Объект для загрузки файлов
        self.upload = VkUpload(self.vk)

        # Объект для обработки событий
        self.longpoll = VkLongPoll(self.vk, wait=20)

        # Слушатели события новых сообщений
        self.eventMessageNew = []
        self.eventReactionNew = []


    def callEvents(self, l, params):
        """
        Метод для вызова слушателей события
        """
        for func in l:
            func(*params)


    def write_msg(self, user_id, message, buttons=None, files=None):
        """
        Метод для отправки сообщений пользователю
        """
        if not files is None:
            files_data = []
            for file in files:

                if file["type"] == "photo":
                    photo = self.upload.photo_messages(file["path"])
                    owner_id = photo[0]['owner_id']
                    photo_id = photo[0]['id']
                    access_key = photo[0]['access_key']
                    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                    files_data += [attachment]

            files = ",".join(files_data)


        self.vk.method('messages.send', {
            'user_id': user_id, 
            'message': message, 
            'attachment': files,
            'random_id': get_random_id(),
            'dont_parse_links': 1,
        })


    def loop(self):
        """
        Метод запускающий цикл обработки сообщений 
        """
        for event in self.longpoll.listen():
            try:
                # Событие нового сообщения
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        self.callEvents(self.eventMessageNew, [self, event.user_id, event.text])


            except Exception as e:
                print("vk exception", e)
                message = "Произошла неожиданная ошибка. Я не смогу помочь вам прямо сейчас."
                self.write_msg(event.user_id, message)


