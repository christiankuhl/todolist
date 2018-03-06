from django.db import migrations

def create_todolists(apps, schema_editor):
    User = apps.get_model("auth", model_name='User')
    TodoList = apps.get_model("lists", model_name="TodoList")
    all_groups = set()
    for u in User.objects.all():
        all_groups = all_groups.union(u.groups.values_list("name", flat=True))
    root = User.objects.get(username="root")
    for group in all_groups:
        TodoList.objects.get_or_create(title=group, creator=root)

class Migration(migrations.Migration):
    dependencies = [
        ('lists', 'create_profiles'),
    ]
    operations = [
         migrations.RunPython(create_todolists),
    ]
