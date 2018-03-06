from django.urls import path

from lists import views

app_name = 'lists'
urlpatterns = [
    path('', views.index, name='index'),
    path('todolist/<int:todolist_id>/', views.todolist, name='todolist'),
    path('todolist/<int:todolist_id>/<str:filter_name>/', views.todolist, name='todolist'),
    path('todolist/<int:todolist_id>/<str:filter_name>/<int:lower>/', views.todolist, name='todolist'),
    path('todolist/<int:todolist_id>/<str:filter_name>/<int:lower>/<int:upper>/', views.todolist, name='todolist'),
    path('todolist/<int:todolist_id>/delete', views.delete_todolist, name='del_todolist'),
    path('todolist/add/', views.add_todolist, name='add_todolist'),
    path('todo/add/<int:todolist_id>/', views.add_todo, name='add_todo'),
    path('todolists/', views.overview, name='overview'),
    path('schedules/', views.schedules, name='schedules'),
    path('schedules/add', views.add_schedule, name='add_schedule'),
    path('schedules/<int:schedule_id>/', views.edit_schedule, name='schedule'),
    path('schedules/<int:schedule_id>/delete', views.delete_schedule, name='del_schedule'),
    path('summary/', views.summary, name='summary'),
    path('summary/<int:datefrom>/', views.summary, name='summary'),
    path('summary/<int:datefrom>/<int:dateto>/', views.summary, name='summary'),
    path('stats/', views.user_stats, name='user_stats'),
    path('todo/', views.all_todos, name='todos'),
    path('todo/<str:filter_name>/', views.free_selection, name='todos'),
    path('todo/<str:filter_name>/<int:lower>/', views.free_selection, name='todos'),
    path('todo/<str:filter_name>/<int:lower>/<str:filter_name2>', views.free_selection, name='todos'),
    path('todo/<str:filter_name>/<int:lower>/<int:upper>/', views.free_selection, name='todos'),
    path('todo/<str:filter_name>/<str:filter_name2>/<int:lower2>/', views.free_selection, name='todos'),
    path('todo/<str:filter_name>/<int:lower>/<str:filter_name2>/<int:lower2>', views.free_selection, name='todos'),
]
