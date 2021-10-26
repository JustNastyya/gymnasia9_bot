hello_reply_ms = '''Вы можете посмотреть рассписание на сегодня или на завтра или изменить \
параметры рассылки и ваш класс в настройках'''

hello_reply_if_not_reg = '''Приветствую. У меня Вы можете посмотреть рассписание на сегодня или на завтра, \
а так же узнать о книгах в нашей библиотеке, но \
сначала я хотел бы узнать ваш класс'''

settings_text = 'Тут вы можете изменить свой класс или включить/выключить рассылку рассписания'

list_of_commands = [
    'settings', 'schedule_for_tomorrow',
    'schedule_for_today', 'book_search',
    'books_in_category'
    ]

commands_text = """
Вот такие команды я знаю:

    /settings - список моих настроек
    /schedule_for_today - узнать рассписание на сегодня
    /schedule_for_tomorrow - узнать рассписание на завтра
    /book_search - поиск книги по названию в библиотеке
    /books_in_category список всех книг по категориям
"""


def good_looking_schedule(schedule):
    # {'08:00 - 08:40': 'История', ...}
    res = '\n'.join([
        key + ': ' + schedule[key]
        for key in schedule.keys()
        ])
    return res
