from util import Singleton
from django.db import models
from django.contrib.auth.models import User
import datetime

class Holiday(models.Model):
    date = models.DateField(auto_now=False)
    description = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, null=True, related_name='+', on_delete=models.SET_NULL)
    class Meta:
        ordering = ("date",)

class Holidays(metaclass=Singleton):
    def __init__(self):
        self.refresh()
    def refresh(self):
        self.holidays = Holiday.objects.filter(date__gte=datetime.datetime.now().date()).values_list("date", flat=True)
    def __contains__(self, item):
        return item in self.holidays
