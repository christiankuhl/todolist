from django.contrib.auth.models import User

from rest_framework import permissions, viewsets

from api.serializers import UserSerializer, TodoListSerializer, TodoSerializer
from lists.models import TodoList, Todo


class IsAuthorizedOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `creator` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # If the object doesn't have a creator (i.e. anon) allow all methods.
        if not obj.creator:
            return True
        # Instance must have an attribute named `creator`.
        access_by_creator = (obj.creator == request.user)
        if isinstance(obj, TodoList):
            todolist_title = obj.title
        elif isinstance(obj, Todo):
            todolist_title = obj.todolist.title
        user_groups = request.user.groups.values_list("name", flat=True)
        authorized_group = (todolist_title in user_groups)
        return access_by_creator or authorized_group


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)


class TodoListViewSet(viewsets.ModelViewSet):
    queryset = TodoList.objects.all()
    serializer_class = TodoListSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def perform_create(self, serializer):
        user = self.request.user
        creator = user if user.is_authenticated else None
        serializer.save(creator=creator)


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = (IsAuthorizedOrReadOnly,)

    def perform_create(self, serializer):
        user = self.request.user
        creator = user if user.is_authenticated else None
        serializer.save(creator=creator)
