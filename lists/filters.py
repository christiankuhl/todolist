from calendar_util.util import last_monday, next_friday, weeknumbers
from calendar_util.util import DATE_FORMAT
from datetime import datetime
from lists.models import TodoList
import calendar as cal

class Filter(object):
    overrule_title = False
    def __init__(self, title=None, callable=lambda todo: True, **kwargs):
        self.title = title
        self.callable = callable
    def __call__(self, todo):
        return self.callable(todo)
    def __or__(self, other):
        title = " or ".join([self.title, other.title])
        callable = lambda todo: self(todo) or other(todo)
        return Filter(title, callable)
    def __and__(self, other):
        title = ", ".join([self.title, other.title])
        callable = lambda todo: self(todo) and other(todo)
        return Filter(title, callable)
    def __not__(self):
        title = "Not " + self.title
        callable = lambda todo: not self(todo)
        return Filter(title, callable)

class month(Filter):
    def __init__(self, lower=None, upper=None, **kwargs):
        today = datetime.now().date()
        year = today.year
        if not lower:
            self.datefrom = today.replace(day=1)
            self.title = "This Month"
            self.overrule_title = self.title + "'s Tasks"
        else:
            self.datefrom = datetime(year=year, month=lower, day=1).date()
        self.title = self.datefrom.strftime("%B")
        if not upper:
            month = self.datefrom.month
        else:
            month = upper
        day = cal.monthrange(year, month)[1]
        self.dateto = datetime(year=year, month=month, day=day).date()
        if upper:
            self.title += " to {}".format(self.dateto.strftime("%B"))
    def __call__(self, todo):
        return self.datefrom <= todo.due_date.date() <= self.dateto

class year(Filter):
    def __init__(self, lower=None, upper=None, **kwargs):
        today = datetime.now().date()
        if not lower:
            self.datefrom = today.replace(month=1, day=1)
        else:
            self.datefrom = datetime(year=lower, month=1, day=1).date()
        self.title = str(self.datefrom.year)
        if not upper:
            self.dateto = self.datefrom.replace(month=12, day=31)
        else:
            self.dateto = datetime(year=upper, month=12, day=31).date()
            self.title += " to {}".format(upper)
    def __call__(self, todo):
        return self.datefrom <= todo.due_date.date() <= self.dateto

class day(Filter):
    def __init__(self, lower=None, upper=None, **kwargs):
        today = datetime.now().date()
        if not lower:
            self.datefrom = today
            self.title = "Today"
            self.overrule_title = self.title + "'s Tasks"
        else:
            self.datefrom = datetime.strptime(str(lower), "%Y%m%d").date()
            self.title = self.datefrom.strftime(DATE_FORMAT)
        if not upper:
            self.dateto = self.datefrom
        else:
            self.dateto = datetime.strptime(str(upper), "%Y%m%d").date()
            self.title += " to {}".format(self.dateto.strftime(DATE_FORMAT))
    def __call__(self, todo):
        return self.datefrom <= todo.due_date.date() <= self.dateto

class week(Filter):
    def __init__(self, lower=None, upper=None, **kwargs):
        today = datetime.now().date()
        year = today.year
        week_dict = weeknumbers(year)
        if not lower:
            self.datefrom = last_monday()
            self.title = "This Week"
            self.overrule_title = self.title + "'s Tasks"
            lower = last_monday().isocalendar()[1]
        else:
            self.datefrom = min(week_dict[lower])
            self.title = "Week {}".format(lower)
        if not upper:
            self.dateto = max(week_dict[lower])
        else:
            self.dateto = max(week_dict[upper])
            self.title += " to {}".format(upper)
    def __call__(self, todo):
        return self.datefrom <= todo.due_date.date() <= self.dateto

# class today(Filter):
#     overrule_title = True
#     def __init__(self):
#         self.title = "Today's Tasks"
#     def __call__(self, todo):
#         return todo.due_date.date() == datetime.now().date()

# class this_week(Filter):
#     overrule_title = True
#     def __init__(self):
#         self.title = "This Week's Tasks"
#     def __call__(self, todo):
#         return last_monday() <= todo.due_date.date() <= next_friday()

class todolist(Filter):
    def __init__(self, lower, **kwargs):
        self.title = TodoList.objects.get(pk=lower).title
        self.id = lower
    def __call__(self, todo):
        return todo.todolist.id == self.id

class all(Filter):
    overrule_title = True
    def __init__(self, **kwargs):
        self.title = "All Tasks"
    def __call__(self, todo):
        return True
