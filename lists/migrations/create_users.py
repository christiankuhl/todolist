from django.db import migrations
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import json

def create_users(apps, schema_editor):
    User = apps.get_model("auth", model_name='User')
    UserModel = get_user_model()
    Profile = apps.get_model("lists", "Profile")
    with open("initial_users.json", "r") as file_handle:
        initial_users = json.load(file_handle)
    for u in initial_users:
        if not UserModel.objects.filter(username=u["username"]).exists():
            user = UserModel.objects.create_user(u["username"], password="welcome123")
        else:
            user = UserModel.objects.get(username=u["username"])
        user.is_superuser = u["is_superuser"]
        user.is_staff = u["is_staff"]
        user.email = u["email"]
        user.first_name = u["first_name"]
        user.last_name = u["last_name"]
        user.save()
        for group_name in u["groups"]:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                group.save()
            group.user_set.add(user)
            group.save()
    for u in User.objects.all():
        if not hasattr(u, 'profile'):
            Profile.objects.create(user=u)
            u.save()

class Migration(migrations.Migration):
    dependencies = [
        ('lists', '0003_auto_20180222_2059'),
    ]
    operations = [
         migrations.RunPython(create_users),
    ]
