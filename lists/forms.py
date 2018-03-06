from django import forms
from lists.models import Todo, Schedule
from calendar_util.util import next_workday, DATETIME_FORMAT, to_string
from django.core.exceptions import ValidationError
import datetime

def widget_attrs(placeholder):
    return {'class': 'u-full-width', 'placeholder': placeholder}

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['description', 'due_date']
        widgets = {'description': forms.TextInput(attrs={'placeholder': 'Enter your todo',
                                                         'class': 'u-full-width'}),
                    'due_date': forms.DateTimeInput(attrs={'placeholder': to_string(next_workday()),
                                                           'id': 'duedate'},
                                                    format=DATETIME_FORMAT)}


class TodoListForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs=widget_attrs('Enter a title to start a new (personal) todolist')),
        label = "",
        max_length = 128)

class TodoListDeleteForm(forms.Form):
    pass

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["description", "frequency", "offset", "todolist", "active"]
