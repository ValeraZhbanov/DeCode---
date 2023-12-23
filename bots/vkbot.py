# -*- coding: cp1251 -*-

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload
from vk_api.utils import get_random_id


class VkBot:

    def __init__(self, token):

        # ������ ��� ���������� �������� � ��
        self.vk = vk_api.VkApi(token=token)

        # ������ ��� �������� ������
        self.upload = VkUpload(self.vk)

        # ������ ��� ��������� �������
        self.longpoll = VkLongPoll(self.vk, wait=20)

        # ��������� ������� ����� ���������
        self.eventMessageNew = []
        self.eventReactionNew = []


    def callEvents(self, l, params):
        """
        ����� ��� ������ ���������� �������
        """
        for func in l:
            func(*params)


    def write_msg(self, user_id, message, buttons=None, files=None):
        """
        ����� ��� �������� ��������� ������������
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
        ����� ����������� ���� ��������� ��������� 
        """
        for event in self.longpoll.listen():
            try:
                # ������� ������ ���������
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        self.callEvents(self.eventMessageNew, [self, event.user_id, event.text])


            except Exception as e:
                print("vk exception", e)
                message = "��������� ����������� ������. � �� ����� ������ ��� ����� ������."
                self.write_msg(event.user_id, message)


