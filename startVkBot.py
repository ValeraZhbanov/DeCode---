 #-*- coding: cp1251 -*-


from bots import vkbot
from bot import handlers

# ����� ������� 
vktoken = "vk1.a.VWzuc5ckgAcjLCP5Vm3fu9gfRz0g8EPFQBlmjt0JQahcZsczqrGqjEIHDU6ox1eD_XMT_PLkzNUmzwN_rXNOJRJzQwI3pv93YYZo1Fq8xoGLY-uWbHKo5O3FJqECrxocO5BK8eehfaKIyvnKUU14Dyz187EBI6eURFh3WW2-C9rxgmAUs-wtUu064hLTfE8guR4y328sHQSWB2eSC0e4ng"

# �������� ���������� � �� �����
vkbot = vkbot.VkBot(vktoken)

# ��������� ������������
vkbot.eventMessageNew += [handlers.newMessageEvent]

# ������ ����� ������ ������� � ��������� �������
print("Init", "VkBot �������.")
vkbot.loop()





