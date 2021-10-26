import requests
import datetime
from data.consts import days_of_the_week
from data.config import path_to_api_server


class APIRequestsSchedule:
    def __init__(self):
        self.path_to_server = path_to_api_server

    def get_list_of_classes(self):
        path = self.path_to_server + f"/classes_in_paralel"
        return requests.get(path).json()
    
    def _get_day(self):
        return datetime.datetime.today().weekday()

    def get_schedule_for_today(self, clas):
        day = self._get_day()
        if day == 6:
            return "Сегодня выходной"

        day = days_of_the_week[day]
        path = self.path_to_server + f"/schedule/{clas}&{day}"
        data = requests.get(path).json()
        return data

    def get_schedule_for_tomorrow(self, clas):
        day = self._get_day() + 1
        if day == 7:
            day = 0
        if day == 6:
            return "Завтра выходной"

        day = days_of_the_week[day]
        path = self.path_to_server + f"/schedule/{clas}&{day}"
        data = requests.get(path).json()
        return data


class APIRequestsLibrary:
    def __init__(self):
        self.path_to_server = path_to_api_server
        path = self.path_to_server + '/library/literature_categories'
        self.literature_categories = requests.get(path).json()

    def match_books_request(self, request):
        path = self.path_to_server + f'/library/match_books/{request}'
        matched_books = requests.get(path).json()
        return matched_books  # {book1: clas, book2:clas...}

    def get_books_in_category(self, category, in_stock):
        path = self.path_to_server + f'/library/books_in_category/{category}&in_stock={in_stock}'
        books = requests.get(path).json()
        return books  # {book1: clas, book2:clas...}

    def get_list_of_categories(self):
        return self.literature_categories
