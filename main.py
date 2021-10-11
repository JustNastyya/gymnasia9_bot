from data.user_bd import UsersBD
import telebot
from data.config import *
from data.api_request import *
from data.texts_for_dialog import *
import schedule
from data.consts import *
from threading import Thread
from time import sleep
import time
from multiprocessing.context import Process
import schedule


# main variables
bot = telebot.TeleBot(token)
users = UsersBD()
api_requests = APIRequests()

# init keyboards
list_of_classes_available = [str(i) for i in range(8, 11 + 1)]
class_list_keyboard = telebot.types.ReplyKeyboardMarkup(True)
class_list_keyboard.row(*list_of_classes_available)

amount_of_letters_in_each_paralel = api_requests.get_list_of_classes()
keyboard_letters_for_each_paralel = {
    clas: telebot.types.ReplyKeyboardMarkup(True).row(*[
            i for i in 'АБВГДЕ'[:amount_of_letters_in_each_paralel[clas]] 
        ])
    for clas in amount_of_letters_in_each_paralel.keys()
}

main_keyboard = telebot.types.ReplyKeyboardMarkup(True)
main_keyboard.row(
    'Рассписание на сегодня',
    'Рассписание на завтра',
    'Настройки'
)

settings_keyboard = telebot.types.ReplyKeyboardMarkup(True)
settings_keyboard.row(
    'сменить класс',
    'включить/выключить рассылку рассписания',
    'обратно'
)

# variable for next step handlers
isRunning = False
number = ''
letter = ''

# functions for next step handlers

def change_clas(message):
    msg = bot.send_message(message.chat.id, hello_reply_if_not_reg,
                        reply_markup=class_list_keyboard)
    bot.register_next_step_handler(msg, ask_clas)
    isRunning = True


def ask_clas(message):
    global isRunning, number
    if message.text.isdigit() and message.text in list_of_classes_available:
        number = message.text
        msg = bot.send_message(message.chat.id, 'Прекрасно, а какая буква?',
                        reply_markup=keyboard_letters_for_each_paralel[number])
        bot.register_next_step_handler(msg, ask_letter)
    else:
        bot.send_message(message.chat.id,
            'вы неправильно Ввели значение класса (внизу есть панель с выбором класса)')
        msg = bot.send_message(message.chat.id, hello_reply_if_not_reg,
                        reply_markup=class_list_keyboard)
        bot.register_next_step_handler(msg, ask_clas)


def ask_letter(message):
    global isRunning
    if len(message.text) == 1 and message.text in 'АБВГДЕ':
        letter = message.text
        bot.send_message(message.chat.id, 'Я вас запомнил')
        bot.send_message(message.chat.id, hello_reply_ms,
                        reply_markup=main_keyboard)
        nickname = message.from_user.username.lower()
        users.add_user(nickname, number + letter, message.chat.id)
        isRunning = False
    else:
        bot.send_message(message.chat.id,
            'вы неправильно Ввели значение буквы класса (внизу есть панель с выбором)')
        msg = bot.send_message(message.chat.id, hello_reply_if_not_reg,
                        reply_markup=class_list_keyboard)
        bot.register_next_step_handler(msg, ask_clas)


# send schedule

def send_schedule(nickname, chat_id, for_today=True):
    # if for_today is false then the schedule will be sent for tomorror
    clas = users.get_clas(nickname)
    if for_today:
        schedule = api_requests.get_schedule_for_today(clas)
    else:
        schedule = api_requests.get_schedule_for_tomorrow(clas)
    if type(schedule) == str:
        bot.send_message(chat_id, schedule, reply_markup=main_keyboard)  # Сегодня - выходной
    else:
        answer = 'Вот рассписание \n\n' + good_looking_schedule(schedule)
        bot.send_message(chat_id, answer, reply_markup=main_keyboard)


def send_schedule_to_all_users():
    for user, chat_id in users.get_list_of_all_users():
        send_schedule(user, chat_id)


def schedule_checker():  # 
    while True:
        schedule.run_pending()
        sleep(1)


schedule.every(1).minutes.do(send_schedule_to_all_users)
# schedule.every().day.at("08:00").do(send_schedule_to_all_users)
 
 
class ScheduleMessage():
    def try_send_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
 
    def start_process():
        p1 = Process(target=ScheduleMessage.try_send_schedule, args=())
        p1.start()


# message handlers

@bot.message_handler(commands = ['start'])
def start_message(message):
    nickname = message.from_user.username.lower()
    if users.check_user_in_bd(nickname):
        bot.send_message(message.chat.id, hello_reply_ms,
                        reply_markup=main_keyboard)
    else:
        change_clas(message)


@bot.message_handler(content_types = ['text'])
def send_text(message):  # if users message is a text
    msg = message.text.lower()

    if msg == 'привет':
        bot.send_message(message.chat.id, 'Привет)', reply_markup=main_keyboard)

    elif msg == 'рассписание на сегодня':
        nickname = message.from_user.username.lower()
        send_schedule(nickname, message.chat.id)

    elif msg == 'рассписание на завтра':
        nickname = message.from_user.username.lower()
        send_schedule(nickname, message.chat.id, for_today=False)

    elif msg == 'настройки':
        bot.send_message(message.chat.id, settings_text, reply_markup=settings_keyboard)

    elif msg == 'включить/выключить рассылку рассписания':
        nickname = message.from_user.username.lower()
        res_text = users.turn_notifications_off_on(nickname)
        bot.send_message(message.chat.id, res_text, reply_markup=settings_keyboard)
    
    elif msg == 'сменить класс':
        change_clas(message)

    elif msg == 'обратно':
        bot.send_message(message.chat.id, 'Вы вернулить в главное меню', reply_markup=main_keyboard)
    
    else:
        bot.send_message(message.chat.id, 'Таких команд я не знаю', reply_markup=main_keyboard)


if __name__ == '__main__':
    ScheduleMessage.start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass

"""
if __name__ == '__main__':
    Time_reports.start_process()
    try:
        bot.polling(none_stop=True, interval = 0)
    except:
        pass

if __name__ == "__main__":
    schedule.every().day.at(SCHEDULE_TIME).do(send_schedule_to_all_users)
    Thread(target=schedule_checker).start()  # без понятия как работает, но нужен для шедула

    bot.polling(none_stop=True)
"""