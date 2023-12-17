 #-*- coding: UTF-8 -*-


from bots import vkbot
from bot import handlers

# Токен доступа 
vktoken = ""
# Создание соединения с вк ботом
vkbot = vkbot.VkBot(vktoken)

# Установка обработчиков
vkbot.eventMessageNew += [handlers.newMessageEvent]

# Запуск цикла опроса сервера и обработки событий
print("Init", "VkBot запущен.")
vkbot.loop()





