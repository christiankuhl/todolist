from django.db import migrations
from django.contrib.auth.models import User

def create_profiles(apps, schema_editor):
    Profile = apps.get_model("lists", "Profile")
    for u in User.objects.all():
        if not hasattr(u, 'profile'):
            Profile.objects.create(user=u)
            u.save()

class Migration(migrations.Migration):
    dependencies = [
        ('lists', 'create_users'),
    ]
    operations = [
         migrations.RunPython(create_profiles),
    ]
