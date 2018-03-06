from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from lists.forms import TodoForm, TodoListForm
from lists.models import Todo, TodoList
from unittest import skip
from calendar_util.constants import THE_DATE


class ListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'test')
        self.todolist = TodoList(title='test title', creator=self.user)
        self.todolist.save()
        self.todo = Todo(description='save todo',
                         due_date=THE_DATE,
                         todolist_id=self.todolist.id,
                         creator=self.user)
        self.todo.save()
        self.client.login(username='test', password='test')
    def tearDown(self):
        self.client.logout()
        self.user.delete()
        self.todolist.delete()
        self.todo.delete()
    def test_get_index_page(self):
        response = self.client.get(reverse('lists:index'))
        self.assertTemplateUsed(response, 'lists/index.html')
        self.assertIsNotNone(response.context['greeting'])
    def test_get_todolist_view(self):
        response = self.client.get(reverse('lists:todolist', kwargs={'todolist_id': self.todolist.id}))
        self.assertTemplateUsed(response, 'lists/todolist.html')
        self.assertIsInstance(response.context['form'], TodoForm)
    def test_add_todo_to_todolist_view(self):
        response = self.client.post(reverse('lists:todolist', kwargs={'todolist_id': self.todolist.id}),
                                            {'description': 'test'})
        self.assertTemplateUsed(response, 'lists/todolist.html')
        self.assertIsInstance(response.context['form'], TodoForm)
        self.assertContains(response, 'test')
    def test_get_todolist_overview(self):
        response = self.client.get(reverse('lists:overview'))
        self.assertTemplateUsed(response, 'lists/overview.html')
        self.assertIsInstance(response.context['form'], TodoListForm)
    def test_get_todolist_overview_redirect_when_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('lists:overview'))
        self.assertRedirects(response, '/auth/login/?next=/todolists/')
    def test_add_todolist_to_todolist_overview(self):
        response = self.client.post(reverse('lists:overview'), {'title': 'some title'})
        self.assertRedirects(response, '/todolist/add/',
                             target_status_code=302,
                             fetch_redirect_response=False)
    def test_filter_usage(self):
        
