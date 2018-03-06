from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.utils import timezone
from django.urls import reverse
from calendar_util.util import *
from calendar_util.constants import TIMEZONE
from util import MenuItem

class DueDateField(models.DateTimeField):
    default = datetime.datetime(9999, 12, 31, 0, 0, tzinfo=TIMEZONE)
    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            if value.hour == 0 and value.minute == 0 and value.second == 0:
                value = value.replace(hour=17, tzinfo=TIMEZONE)
            return value
        elif not value:
            return next_workday()
        else:
            return parse_duedate(value)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def todolists(self):
        return TodoList.objects.filter(Q(creator=self.user) |
                                       Q(title__in=self.user.groups.values_list('name',flat=True)))
    def menuitems(self):
        result = []
        result.append(MenuItem(text="Your Todolists", url=reverse("lists:overview")))
        result.append(MenuItem(text="Today's Tasks", url=reverse("lists:todos", args=["day"])))
        result.append(MenuItem(text="This Week", url=reverse("lists:todos", args=["week"])))
        user_groups = self.user.groups.values_list('name',flat=True)
        if "Admin" in user_groups:
            result.append(MenuItem(text="Summary Report", url=reverse("lists:summary")))
            result.append(MenuItem(text="User Statistic", url=reverse("lists:user_stats")))
        else:
            result = result + [MenuItem(text=t.title, url=reverse("lists:todolist", args=[t.id,]))
                                        for t in TodoList.objects.filter(title__in=user_groups)]
        if self.user.is_staff:
            result.append(MenuItem(text="Schedules", url=reverse("lists:schedules")))
            result.append(MenuItem(text="Admin", url="/admin"))
        return result

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class TodoList(models.Model):
    title = models.CharField(max_length=128, default='untitled')
    created_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    class Meta:
        ordering = ('created_at',)
    def __str__(self):
        return self.title
    def count(self):
        return self.todos.count()
    def count_finished(self):
        return self.todos.filter(is_finished=True).count()
    def count_open(self):
        return self.todos.filter(is_finished=False).count()
    def last_change(self):
        last_changes_todos = self.todos.values_list("last_change", flat=True)
        if last_changes_todos:
            return max(last_changes_todos)
        else:
            return self.created_at

class Todo(models.Model):
    description = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True)
    is_finished = models.BooleanField(default=False)
    due_date = DueDateField(auto_now=False, blank=True)
    creator = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    done_by = models.ForeignKey(User, null=True, related_name='todos', on_delete=models.SET_NULL)
    todolist = models.ForeignKey(TodoList, related_name='todos', on_delete=models.CASCADE)
    from_schedule = models.ForeignKey("Schedule", on_delete=models.SET_NULL, null=True)
    class Meta:
        ordering = ('due_date',)
    def __str__(self):
        return self.description
    def close(self):
        self.finished_at = datetime.datetime.now().replace(tzinfo=TIMEZONE)
        self.is_finished = True
        self.save()
    def reopen(self):
        self.finished_at = None
        self.is_finished = False
        self.save()

class MockAll(object):
    def __init__(self, instance):
        self.instance = instance
    def all(self):
        return self.instance._todos

class TmpTodoList(object):
    def __init__(self, title, creator, id):
        self.title = title
        self.creator = creator
        self._todos = []
        self.todos = MockAll(self)
        self.id = id
    def count_open(self):
        return len([t for t in self._todos if not t.is_finished])
    def count_finished(self):
        return len([t for t in self._todos if t.is_finished])
    def add(self, todo):
        self._todos.append(todo)

class Schedule(models.Model):
    FREQUENCY_CHOICES = ((DAILY, "daily"), (MONTHLY, "monthly"),
                         (QUARTERLY, "quarterly"), (YEARLY, "yearly"))
    GENERATION_PERIODS = {DAILY: (5, (1, DAILY)),
                          MONTHLY: (3, (1, MONTHLY)),
                          QUARTERLY: (4, (3, MONTHLY)),
                          YEARLY: (1, (1, YEARLY))}
    description = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    frequency = models.CharField(max_length=3, choices=FREQUENCY_CHOICES, default=DAILY)
    offset = models.IntegerField()
    creator = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)
    todolist = models.ForeignKey(TodoList, on_delete=models.CASCADE, null=False)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ("created_at",)
    def __str__(self):
        return self.description

def todos_from_schedule(schedule):
    assert schedule.active
    dates_to_generate, (shift, unit) = Schedule.GENERATION_PERIODS[schedule.frequency]
    start_date = next_ultimo(schedule.frequency)
    target_date = start_date
    root = User.objects.get(username="root")
    todos = []
    for _ in range(dates_to_generate):
        if (is_workday(target_date) and schedule.frequency == DAILY) or schedule.frequency != DAILY:
            due_date = workday_offset(target_date, schedule.offset)
            description = schedule.description + " " + specstr(schedule.frequency, target_date)
            todo = Todo(description=description, creator=root, from_schedule=schedule,
                        todolist=schedule.todolist, due_date=due_date)
            todos.append(todo)
        target_date = shift_date(target_date, shift, unit)
    existing_todos = schedule.todolist.todos.filter(Q(from_schedule=schedule))
    keys = {(t.description, t.due_date.date()) for t in existing_todos}
    for todo in todos:
        key = (todo.description, todo.due_date.date())
        if key not in keys:
            todo.save()

def update_todos():
    schedules = Schedule.objects.filter(active=True)
    for schedule in schedules:
        todos_from_schedule(schedule)
