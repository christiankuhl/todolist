from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, Http404
from lists.models import TodoList, Todo, TmpTodoList, Schedule
from django.contrib.auth.models import Group
from django.contrib import messages
from lists.forms import TodoForm, TodoListForm, ScheduleForm
from util import MenuItem
import lists.filters

def index(request):
    if request.user.is_authenticated:
        greeting = " ".join([request.user.first_name, request.user.last_name])
    else:
        greeting = "to the GC-MC Tasklist"
    return render(request, 'lists/index.html', {'greeting': greeting})

staff_only = user_passes_test(lambda user: user.is_staff)

@login_required
def todolist(request, todolist_id, filter_name=None, **kwargs):
    todolist = get_object_or_404(TodoList, pk=todolist_id)
    if filter_name:
        try:
            filter_instance = lists.filters.todolist(todolist_id) & getattr(lists.filters, filter_name)(**kwargs)
        except AttributeError:
            raise Http404
        todolist = queryToDo(title=filter_instance.title,
                             creator=request.user,
                             filter_instance=filter_instance,
                             id=todolist_id)
    functions = [MenuItem(url=reverse("lists:todolist", args=[todolist_id]),
                          text="All"),
                 MenuItem(url=reverse("lists:todolist", args=[todolist_id, "day"]),
                          text="Today"),
                 MenuItem(url=reverse("lists:todolist", args=[todolist_id, "week"]),
                          text="This Week"),
                 MenuItem(url=reverse("lists:todolist", args=[todolist_id, "month"]),
                          text="This Month"),]
    if request.method == 'POST':
        redirect('lists:add_todo', todolist_id=todolist_id)
    return render(request, 'lists/todolist.html', {'todolist': todolist,
                                                   'form': TodoForm(),
                                                   'functions': functions})

@login_required
def add_todo(request, todolist_id):
    if request.method == 'POST':
        todolist = get_object_or_404(TodoList, pk=todolist_id)
        form = TodoForm(request.POST)
        if form.is_valid():
            user = request.user
            due_date = form.cleaned_data['due_date']
            todo = Todo(description=request.POST['description'],
                        todolist_id=todolist_id,
                        due_date=due_date,
                        creator=user)
            todo.save()
            return redirect('lists:todolist', todolist_id=todolist_id)
        else:
            return render(request, 'lists/todolist.html',
                                        {'form': form, 'todolist': todolist})
    return redirect('lists:index')


@login_required
def overview(request):
    if request.method == 'POST':
        return redirect('lists:add_todolist')
    return render(request, 'lists/overview.html', {'form': TodoListForm()})

@login_required
def add_todolist(request):
    if request.method == 'POST':
        form = TodoListForm(request.POST)
        if form.is_valid():
            user = request.user
            title = request.POST['title']
            is_group_list = (title in Group.objects.all().values_list("name", flat=True))
            title_exists = TodoList.objects.filter(title=title).exists()
            if is_group_list and title_exists and not user.is_superuser:
                messages.error(request, "A todolist with title {} already exists!".format(title))
                return render(request, 'lists/overview.html', {'form': form})
            todolist = TodoList(title=title, creator=user)
            todolist.save()
            return redirect('lists:todolist', todolist_id=todolist.id)
        else:
            return render(request, 'lists/overview.html', {'form': form})

    return redirect('lists:index')

@login_required
def delete_todolist(request, todolist_id):
    if request.method == "GET":
        user = request.user
        todolist = get_object_or_404(TodoList, pk=todolist_id)
        has_permission = user.has_perm("lists.delete_todolist")
        is_owner = (todolist.creator == request.user)
        if has_permission or is_owner:
            todolist.delete()
            return redirect("lists:index")
    return redirect('lists:todolist', todolist_id=todolist_id)

def queryToDo(title, creator, filter_instance, id=None):
    todolist = TmpTodoList(title=title, creator=creator, id=id)
    user_lists = creator.profile.todolists()
    for tmp_list in user_lists:
        for todo in tmp_list.todos.all():
            if filter_instance(todo):
                todolist.add(todo)
    return todolist

@login_required
def free_selection(request, filter_name, lower=None, filter_name2=None, lower2=None, **kwargs):
    try:
        filter_instance = getattr(lists.filters, filter_name)(lower, **kwargs)
    except AttributeError:
        raise Http404
    title = filter_instance.title
    if not filter_instance.overrule_title:
        title = "All Tasks, {}".format(title)
    else:
        title = filter_instance.overrule_title
    if filter_name2:
        try:
            filter_instance2 = getattr(lists.filters, filter_name2)(lower2)
        except AttributeError:
            raise Http404
        filter_instance = filter_instance & filter_instance2
        title = filter_instance.title
    todolist = queryToDo(title=title, creator=request.user,
                         filter_instance=filter_instance)
    functions = build_menu(todolist, filter_name, lower, filter_name2)
    return render(request, 'lists/todolist.html',
                  {'todolist': todolist, 'form': None, 'functions': functions})

def build_menu(todolist, filter_name, lower, filter_name2, base_url="lists:todos"):
    todolists = {t.todolist for t in todolist.todos.all()}
    todo_menuitems = []
    for t in todolists:
        if filter_name:
            if lower:
                args = [filter_name, lower, "todolist", t.id]
            else:
                args = [filter_name, "todolist", t.id]
        else:
            args = ["todolist", t.id]
        todo_menuitems.append(MenuItem(url=reverse(base_url, args=args), text=t.title))
    if filter_name:
        if filter_name2:
            if lower:
                args = [filter_name, lower]
            else:
                args = [filter_name]
            time_args = args
        else:
            args = []
            if lower:
                time_args = [filter_name, lower]
            else:
                time_args= [filter_name]
        all_menuitem = [MenuItem(url=reverse(base_url, args=args), text="All")]
    else:
        all_menuitem = []
        time_args = []
    time_filters = [("day", "Today"), ("week", "This Week"), ("month", "This Month")]
    if filter_name in ["day", "week", "month"] or filter_name2 in ["day", "week", "month"]:
        time_menuitems = []
    else:
        time_menuitems = [MenuItem(url=reverse(base_url, args= time_args + [time]), text=text)
                                                                    for time, text in time_filters]
    if len(todo_menuitems) > 1:
        functions = all_menuitem + time_menuitems + todo_menuitems
    else:
        functions = all_menuitem + time_menuitems
    return functions

@login_required
def all_todos(request):
    todolist = queryToDo(title="All Tasks", creator=request.user,
                         filter_instance=lists.filters.all())
    functions = build_menu(todolist, None, None, None)
    return render(request, 'lists/todolist.html', {'todolist': todolist,
                                                   'form': None,
                                                   'functions': functions})

@login_required
def summary(request):
    pass

@login_required
def user_stats(request):
    pass

@login_required
@staff_only
def schedules(request):
    if request.method == 'POST':
        redirect('lists:add_schedule')
    schedules = Schedule.objects.all()
    return render(request, 'lists/schedule.html', {'schedules': schedules, 'form': ScheduleForm()})

@login_required
@staff_only
def add_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            user = request.user if request.user.is_authenticated else None
            schedule = Schedule(creator=user, **form.cleaned_data)
            schedule.save()
            return redirect('lists:schedules')
        else:
            return render(request, 'lists/schedule.html', {'form': form})

@login_required
@staff_only
def edit_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if request.method == 'GET':
        form = ScheduleForm(instance=schedule)
        return render(request, 'lists/schedule.html', {'form': form, 'schedule': schedule})
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            for field, value in form.cleaned_data.items():
                setattr(schedule, field, value)
            schedule.save()
            return redirect('lists:schedules')
        else:
            return render(request, 'lists/schedule.html', {'form': form, 'schedule': schedule})

@login_required
@staff_only
def delete_schedule(request):
    pass
