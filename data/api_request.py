import requests
from data.data_which_is_actually_from_api import *
import datetime
from data.consts import days_of_the_week


class APIRequests:
    def __init__(self):
        self.path_to_server = ''

    def get_list_of_classes(self):
        path = self.path_to_server + f"//classes_in_paralel"
        # return requests.get(path).json()
        return amount_of_letters_in_each_paralel
    
    def _get_day(self):
        return datetime.datetime.today().weekday()

    def get_schedule_for_today(self, clas):
        day = self._get_day()
        if day == 6:
            return "Сегодня выходной"

        day = days_of_the_week[day]
        path = self.path_to_server + f"/schedule/{clas}/{day}"
        data = {'result': f'рассписание типа на {day}'}  # requests.get(path).json()
        """
        data = {
            'result': {'08:00 - 08:40': 'История', ...}
        }
        """
        return data['result']

    def get_schedule_for_tomorrow(self, clas):
        day = self._get_day() + 1
        if day == 7:
            day = 0
        if day == 6:
            return "Завтра выходной"

        day = days_of_the_week[day]
        path = self.path_to_server + f"/schedule/{clas}/{day}"
        data = {'result': f'рассписание типа на {day}'}  # requests.get(path).json()
        """
        data = {
            'result': {'08:00 - 08:40': 'История', ...}
        }
        """
        return data['result']
