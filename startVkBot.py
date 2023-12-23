 #-*- coding: cp1251 -*-


from bots import vkbot
from bot import handlers

# Токен доступа 
vktoken = "vk1.a.VWzuc5ckgAcjLCP5Vm3fu9gfRz0g8EPFQBlmjt0JQahcZsczqrGqjEIHDU6ox1eD_XMT_PLkzNUmzwN_rXNOJRJzQwI3pv93YYZo1Fq8xoGLY-uWbHKo5O3FJqECrxocO5BK8eehfaKIyvnKUU14Dyz187EBI6eURFh3WW2-C9rxgmAUs-wtUu064hLTfE8guR4y328sHQSWB2eSC0e4ng"

# Создание соединения с вк ботом
vkbot = vkbot.VkBot(vktoken)

# Установка обработчиков
vkbot.eventMessageNew += [handlers.newMessageEvent]

# Запуск цикла опроса сервера и обработки событий
print("Init", "VkBot запущен.")
vkbot.loop()





