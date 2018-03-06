# Generated by Django 2.0.2 on 2018-02-26 22:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import csv
from calendar_util.models import Holiday
from django.contrib.auth.models import User
from datetime import datetime

csv.register_dialect("xlSaveAsCSV", delimiter=';', quoting=csv.QUOTE_NONE, lineterminator='\n', escapechar="\\")

def load_holidays(apps, schema_editor):
    try:
        root = User.objects.get(username="root")
    except:
        root = None
    with open("holidays.csv") as file_handle:
        reader = csv.DictReader(file_handle, dialect="xlSaveAsCSV")
        for line in reader:
            date = datetime.strptime(line['date'], "%d.%m.%Y").date()
            holiday = Holiday(date=date, description=line["description"], creator=root)
            holiday.save()

class Migration(migrations.Migration):
    dependencies = [
        ('calendar_util', '0001_initial'),
    ]
    operations = [
         migrations.RunPython(load_holidays),
    ]