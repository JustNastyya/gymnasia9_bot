import telebot
from data.user_bd import UsersBD
from data.config import *
from data.api_request import *
from data.texts_for_dialog import *
from data.consts import *


# main variables
bot = telebot.TeleBot(token)
users = UsersBD()
api_requests_schedule = APIRequestsSchedule()
api_requests_library = APIRequestsLibrary()

users.check_if_table_exists()

# init keyboards
list_of_classes_available = [str(i) for i in range(8, 11 + 1)]
class_list_keyboard = telebot.types.ReplyKeyboardMarkup(True)
class_list_keyboard.row(*list_of_classes_available)

amount_of_letters_in_each_paralel = api_requests_schedule.get_list_of_classes()
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
    'Найти книгу'
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
        schedule = api_requests_schedule.get_schedule_for_today(clas)
    else:
        schedule = api_requests_schedule.get_schedule_for_tomorrow(clas)
    if type(schedule) == str:
        bot.send_message(chat_id, schedule, reply_markup=main_keyboard)  # Сегодня - выходной
    else:
        answer = 'Вот рассписание \n\n' + good_looking_schedule(schedule)
        bot.send_message(chat_id, answer, reply_markup=main_keyboard)


def send_schedule_to_all_users():
    for user, chat_id in users.get_list_of_all_users():
        send_schedule(user, chat_id)


def send_schedule_for_today(message):
    nickname = message.from_user.username.lower()
    send_schedule(nickname, message.chat.id)


def send_schedule_for_tomorrow(message):
    nickname = message.from_user.username.lower()
    send_schedule(nickname, message.chat.id, for_today=False)


def send_list_of_settings(message):
    bot.send_message(message.chat.id, settings_text, reply_markup=settings_keyboard)


def put_on_off_notifications(message):
    nickname = message.from_user.username.lower()
    res_text = users.turn_notifications_off_on(nickname)
    bot.send_message(message.chat.id, res_text, reply_markup=settings_keyboard)

# message handlers

@bot.message_handler(commands=['start'])
def start_message(message):
    nickname = message.from_user.username.lower()
    if users.check_user_in_bd(nickname):
        bot.send_message(message.chat.id, hello_reply_ms,
                        reply_markup=main_keyboard)
    else:
        change_clas(message)
    bot.send_message(message.chat.id, commands_text, reply_markup=main_keyboard)


@bot.message_handler(commands=list_of_commands)
def commands(message):
    msg = message.text.lower()
    if msg == '/settings':
        send_list_of_settings(message)
    elif msg == '/schedule_for_tomorrow':
        send_schedule_for_tomorrow(message)
    elif msg == '/schedule_for_today':
        send_schedule_for_today(message)
    elif msg == '/book_search':
        pass
    elif msg == '/books_in_category':
        pass


@bot.message_handler(content_types=['text'])
def send_text(message):  # if users message is a text
    msg = message.text.lower()

    if msg == 'привет':
        bot.send_message(message.chat.id, 'Привет)', reply_markup=main_keyboard)

    elif msg == 'рассписание на сегодня':
        send_schedule_for_today(message)

    elif msg == 'рассписание на завтра':
        send_schedule_for_tomorrow(message)

    elif msg == 'найти книгу':
        pass

    elif msg == 'включить/выключить рассылку рассписания':
        put_on_off_notifications(message)
    
    elif msg == 'сменить класс':
        change_clas(message)

    elif msg == 'обратно':
        bot.send_message(message.chat.id, 'Вы вернулить в главное меню', reply_markup=main_keyboard)
    
    else:
        bot.send_message(message.chat.id, commands_text, reply_markup=main_keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True)

