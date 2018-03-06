from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from lists.forms import TodoForm, TodoListForm
from lists.models import Todo, TodoList
from unittest import skip
from calendar_util.constants import THE_DATE

class TodoListFormTests(TestCase):
    def setUp(self):
        self.vaild_form_data = {'title': 'some title'}
        self.too_long_title = {'title': 129 * 'X'}
    def test_valid_input(self):
        form = TodoListForm(self.vaild_form_data)
        self.assertTrue(form.is_valid())
    def test_no_title(self):
        form = TodoListForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'title': [u'This field is required.']})
    def test_empty_title(self):
        form = TodoListForm({'title': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'title': [u'This field is required.']})
    def test_title_too_long(self):
        form = TodoListForm(self.too_long_title)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'title': [u'Ensure this value has at most 128 ' +
                                                        'characters (it has 129).']})

class TodoFormTests(TestCase):
    def setUp(self):
        self.valid_form_data = {'description': 'something to be done',
                                'due_date': THE_DATE}
        self.too_long_description = {'description': 129 * 'X',
                                     'due_date': THE_DATE}
    def test_valid_input(self):
        form = TodoForm(self.valid_form_data)
        self.assertTrue(form.is_valid())
    def test_no_description(self):
        form = TodoForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'description': [u'This field is required.']})
    def test_empty_description(self):
        form = TodoForm({'description': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'description': [u'This field is required.']})
    def test_title_too_long(self):
        form = TodoForm(self.too_long_description)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'description': [u'Ensure this value has at most 128 ' +
                                                            'characters (it has 129).']})
