 #-*- coding: UTF-8 -*-


from bots import vkbot
from bot import handlers

# ����� ������� 
vktoken = ""
# �������� ���������� � �� �����
vkbot = vkbot.VkBot(vktoken)

# ��������� ������������
vkbot.eventMessageNew += [handlers.newMessageEvent]

# ������ ����� ������ ������� � ��������� �������
print("Init", "VkBot �������.")
vkbot.loop()





