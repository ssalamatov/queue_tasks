import time

import datetime


def now():
    return time.strftime('%H:%M:%S')


def time_to_string(_time):
    if type(_time) == datetime.time:
        return str(_time)
    return _time
