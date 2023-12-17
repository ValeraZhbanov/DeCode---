# -*- coding: UTF-8 -*-

import os
import jarowinkler 

import matplotlib.pyplot as plt
import matplotlib.dates
from sql.dbstore import DbStore

from bot import AI
from bot.botgpt import BotGTP
from sql.dbstore import DbStore

# Имя и путь для рабочей директории приложения
BASENAME = os.path.basename(__file__)
PATH = os.path.abspath(__file__).replace(BASENAME, "")

# Языковая модель
botgpt = BotGTP()

# Токинайзер путь
tokenizer_path = os.path.join(PATH, "AI_data", "encoder", "encoder.w2v")
# Модель модерации путь
moderation_path = os.path.join(PATH, "AI_data", "Moderation") + "\\"
# Модель для определения типов путь
qa_path = os.path.join(PATH, "AI_data", "qa") + "\\"

# Токинайзер
tokenizer = AI.PreTokenizer(tokenizer_path)
# Модель модерации 
moderation = AI.ModerationHelper(moderation_path, tokenizer)
# Модель для определения типов
qa = AI.QAHelper(qa_path, tokenizer)


def newMessageEvent(bot, user_id, text):
    """
    Метод для обработки новых сообщений
    """
    print("new message event", user_id, text)

    # Создание аккаунта для нового пользователя
    создать_аккаунт_если_не_существует(user_id)
    # Получаем запрос пользователя или создаем новый если его нет
    код_запроса = получить_запрос(user_id)
    # Сохраняем сообщение
    новое_сообщение(код_запроса, text, 1)

    # Проводим модерацию
    if moderation.normal_text(text) < 0.70:
        return give_an_answer(bot, user_id, код_запроса, """"
Если Вы получили данное сообщение, то Ваш запрос содержит: ненормативную лексику, оскорбление.
Или же контекст сообщения не имеет отношения к работе администрации.
Пожалуйста, переформулируйте свой запрос.""")

    # Определяем коэффициенты типа
    q, a = qa(text)

    # Обрабатываем сообщение соответствующего типа
    if 0.90 < jarowinkler.jarowinkler_similarity(text.lower(), "покажи инструкцию"):
        return process_desc(bot, user_id, код_запроса, text)

    if 0.90 < jarowinkler.jarowinkler_similarity(text.lower(), "покажи статистику"):
        return process_stat(bot, user_id, код_запроса, text)

    if 0.70 < q and a < 0.30:
        return processq(bot, user_id, код_запроса, text)

    if 0.70 < a and q < 0.30:
        return processa(bot, user_id, код_запроса, text)

    # Ответ по умолчанию
    return give_an_answer(bot, user_id, код_запроса, "Не удалось однозначно определить тип обращения. Попробуйте перефразировать и обратится повторно.")



def process_desc(bot, user_id, код_запроса, text):
    """
    Обработчик запроса инструкции
    """
    print("Обработка выдачи инструкции:", text)
    изменить_тип_запроса(код_запроса, 4)

    give_an_answer(bot, user_id, код_запроса, """
🤖 Чат-бот разработан для работы с обращениями и вопросами граждан 🤖

💬 При написании вопроса* Вы получите ответ от чат-бота.

💬 Если Вы хотите внести предложение*, то чат-бот его запишет и выдаст Вам подтверждающее сообщение.

*чат-бот самостоятельно распознает тип сообщения

📊 Для отображения статистики по обращениям необходимо написать чат-боту сообщение «Покажи статистику».

‼ В случае обнаружения в тексте сообщения оскорблений или ненормативной лексики будет выдано соответствующее сообщение. ‼

✅ Все сообщения из чата будут зафиксированы без сохранения конфиденциальных данных.

❗При возникновении ошибок чат-бот отправит Вам соответствующее сообщение. К сожалению, в этом случае Ваше обращение не будет обработано.
""")

    изменить_статус_запроса(код_запроса, 1)
    return



def process_stat(bot, user_id, код_запроса, text):
    """
    Обработчик запроса статистики
    """

    print("Обработка статистики:", text)
    изменить_тип_запроса(код_запроса, 3)

    стат = получить_статистику()

    message = "Всего было " + str(стат["ЧислоЗапросов"]) + " запросов. Из них " + str(стат["ЧислоВопросов"]) + " вопросов и " + str(стат["ЧислоПредложений"]) + " предложений. За статистикой обратились " + str(стат["ЧислоСтатистик"]) + " раз.";

    give_an_answer(bot, user_id, код_запроса, message, files=[{'type': 'photo', 'path': стат["График"]}])

    изменить_статус_запроса(код_запроса, 1)
    return

def processq(bot, user_id, код_запроса, text):
    """
    Обработчик вопросов
    """
    print("Обработка вопроса:", text)
    изменить_тип_запроса(код_запроса, 1)

    give_an_answer(bot, user_id, код_запроса, "Ваш вопрос отправлен на рассмотрение, ожидайте ответа.")
    give_an_answer(bot, user_id, код_запроса, botgpt.generate(text))

    изменить_статус_запроса(код_запроса, 1)
    return

def processa(bot, user_id, код_запроса, text):
    """
    Обработчик предложений
    """
    print("Обработка предложения:", text)

    # Сообщение уже сохранено так что достаточно пометить что этот запрос - предложение
    изменить_тип_запроса(код_запроса, 2)

    give_an_answer(bot, user_id, код_запроса, "Ваше предложение было сохранено. Также Вы можете обратиться с предложением по номеру +7(41136)123456.")

    изменить_статус_запроса(код_запроса, 1)
    return



def give_an_answer(bot, user_id, код_запроса, text, files=None):
    """
    Метод для отправки сообщений бота
    """
    новое_сообщение(код_запроса, text,  0)
    bot.write_msg(user_id, text, files=files)

    
def создать_аккаунт_если_не_существует(id):
    """
    Метод для создания нового аккаунта в базе данных
    """
    аккаунт = DbStore.execute_select_query_one("SELECT * FROM Аккаунты WHERE Код = %(Код)s", {'Код':str(id)})

    if (аккаунт is None):
        DbStore.execute_insert_query("INSERT INTO Аккаунты (Код) VALUES (%s) RETURNING Код", (str(id),))
        print("Создание аккаунта:", id)

    return 

def получить_запрос(user_id):
    """
    Создат запрос если у пользователя нет не обработанного запроса
    """
    запрос = DbStore.execute_select_query_one("SELECT Код FROM Запросы WHERE КодАккаунта = %(КодАккаунта)s AND Статус = 0", {'КодАккаунта':str(user_id)})

    if (запрос is None):
        print("Создание запроса")
        return DbStore.execute_insert_query("INSERT INTO Запросы (КодАккаунта) VALUES (%s) RETURNING Код", (str(user_id),))

    return запрос.Код

def изменить_статус_запроса(id, status):
    """
    Метод для смены статуса запроса
    """
    return DbStore.execute_update_query("UPDATE Запросы SET Статус = %(Статус)s WHERE Код = %(Код)s", {'Код':id, 'Статус':status})

def изменить_тип_запроса(id, type_id):
    """
    Метод смены типа запроса, так как при создании запроса тип ещё не известен и по умолчанию нулл
    """
    return DbStore.execute_update_query("UPDATE Запросы SET КодТипа = %(КодТипа)s WHERE Код = %(Код)s", {'Код':id, 'КодТипа':type_id})

def новое_сообщение(код_запроса, текст,  это_пользователь):
    """
    Метод для создания нового сообщения
    """
    return DbStore.execute_insert_query("INSERT INTO Сообщения (КодЗапроса, Текст, Пользователь) VALUES (%s, %s, %s) RETURNING Код", (код_запроса, текст, это_пользователь))


def получить_статистику():
    """
    Метод для подсчета статистики
    """
    ЧислоЗапросов = DbStore.execute_select_query_one("SELECT count(*) Число FROM Запросы WHERE Статус = 1").Число
    ЧислоВопросов = DbStore.execute_select_query_one("SELECT count(*) Число FROM Запросы WHERE Статус = 1 AND КодТипа = 1").Число
    ЧислоПредложений = DbStore.execute_select_query_one("SELECT count(*) Число FROM Запросы WHERE Статус = 1 AND КодТипа = 2").Число
    ЧислоСтатистик = DbStore.execute_select_query_one("SELECT count(*) Число FROM Запросы WHERE Статус = 1 AND КодТипа = 3").Число
    ЧислоПоДатам = DbStore.execute_select_query_all("""
SELECT 
	CAST(Сообщения.Дата as date) Дата,
	count(*) Число 
FROM Запросы 
INNER JOIN Сообщения ON Сообщения.КодЗапроса = Запросы.Код
INNER JOIN (
	SELECT КодЗапроса, MIN(Дата) Дата
	FROM Сообщения
	GROUP BY КодЗапроса
) ПервоеСообщение ON ПервоеСообщение.КодЗапроса = Запросы.Код
                    AND ПервоеСообщение.Дата = Сообщения.Дата
WHERE Статус = 1 
GROUP BY CAST(Сообщения.Дата as date)
    """)

    axes = plt.subplot(1, 1, 1)
    axes.tick_params(axis='x', labelrotation=55)
    axes.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%d.%m.%Y"))
    plt.plot(list(map(lambda e: e.Дата, ЧислоПоДатам)), list(map(lambda e: e.Число, ЧислоПоДатам)))

    plt.tight_layout()
    plt.grid()

    #plt.title("Число запросов по дням")
    #plt.xlabel("Дни")
    #plt.ylabel("Число запросов")
    plt.savefig('count_exec.png')

    return {
        'ЧислоЗапросов': ЧислоЗапросов, 
        'ЧислоВопросов': ЧислоВопросов, 
        'ЧислоПредложений': ЧислоПредложений, 
        'ЧислоСтатистик': ЧислоСтатистик, 
        'График': 'count_exec.png', 
    }



















