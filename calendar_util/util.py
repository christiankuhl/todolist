from django.core.exceptions import ValidationError
from calendar_util.constants import *
from calendar_util.models import Holidays
from collections import defaultdict
import datetime
from math import ceil
import calendar as cal

cal.setfirstweekday(cal.MONDAY)

def next_friday(date=None):
    if not date:
        date = datetime.datetime.now().date()
    weekday = cal.weekday(year=date.year, month=date.month, day=date.day)
    return (date + datetime.timedelta(days=(4-weekday) % 7))

def last_monday(date=None):
    if not date:
        date = datetime.datetime.now().date()
    weekday = cal.weekday(year=date.year, month=date.month, day=date.day)
    return (date - datetime.timedelta(days=weekday % 7))

def eod_today():
    return datetime.datetime.now().replace(hour=17, minute=0, second=0, tzinfo=TIMEZONE)

def next_workday(date=None):
    if not date:
        date = eod_today()
    weekday = cal.weekday(year=date.year, month=date.month, day=date.day)
    day = date
    while not (day > date and is_workday(day)):
        day = day + datetime.timedelta(days=1)
    return day

def is_workday(day):
    weekday = cal.weekday(year=day.year, month=day.month, day=day.day)
    return (weekday in range(5)) and day.date() not in Holidays()

def to_datetime(date_string, format=DATETIME_FORMAT):
    date = datetime.datetime.strptime(date_string, format).replace(tzinfo=TIMEZONE)
    if format in DATE_INPUT_FORMATS:
        date = date.replace(hour=17, minute=0, second=0)
    return date

def to_string(datetime_obj):
    return datetime_obj.strftime(DATETIME_FORMAT)

def parse_duedate(date_string):
    date = None
    for format in DATETIME_INPUT_FORMATS:
        try:
            date = to_datetime(date_string)
            break
        except:
            continue
    if date:
        return date
    else:
        raise ValidationError('Enter a valid date/time', code='invalid', params={})

def next_ultimo(frequency, today=None):
    if not today:
        today = eod_today()
    if frequency == DAILY:
        return next_workday(today)
    elif frequency == MONTHLY:
        return today.replace(day=cal.monthrange(today.year, today.month)[1])
    elif frequency == QUARTERLY:
        month = 3 * ceil(today.month/3)
        day = cal.monthrange(today.year, month)[1]
        return today.replace(day=day, month=month)
    elif frequency == YEARLY:
        return today.replace(day=31, month=12)

def specstr(frequency, date):
    if frequency == DAILY:
        return date.strftime("%d.%m.")
    elif frequency == MONTHLY:
        return date.strftime("%b")
    elif frequency == QUARTERLY:
        return "Q{}".format(ceil(date.month/3))
    elif frequency == YEARLY:
        return date.strftime("%Y")

def shift_date(date, shift, unit=DAILY):
    if unit == DAILY:
        return date + datetime.timedelta(days=shift)
    elif unit == MONTHLY:
        month = date.month - 1 + shift
        year = date.year + month // 12
        month = month % 12 + 1
        day = min(date.day, cal.monthrange(year, month)[1])
        return date.replace(year=year, month=month, day=day)
    elif unit == YEARLY:
        return date.replace(year=date.year + shift)

def to_workday(date):
    if is_workday(date):
        return date
    else:
        return next_workday(date)

def workday_offset(date, offset):
    if offset == 0:
        return to_workday(date)
    sign = abs(offset) // offset
    steps = 0
    next_date = date
    while steps < abs(offset):
        next_date = shift_date(next_date, sign)
        if is_workday(next_date):
            steps += 1
    return next_date

def weeknumbers(year):
    result = defaultdict(list)
    day = datetime.datetime(year=year, month=1, day=1)
    while day.year == year:
        week = day.isocalendar()[1]
        if day.month == 12 and week == 1:
            break
        result[week].append(day.date())
        day += datetime.timedelta(days=1)
    return result
