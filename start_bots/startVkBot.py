 #-*- coding: cp1251 -*-


from bots import vkbot
from bot import handlers

# ����� ������� 

# �������� ���������� � �� �����
vkbot = vkbot.VkBot(vktoken)

# ��������� ������������
vkbot.eventMessageNew += [handlers.newMessageEvent]

# ������ ����� ������ ������� � ��������� �������
print("Init", "VkBot �������.")
vkbot.loop()





