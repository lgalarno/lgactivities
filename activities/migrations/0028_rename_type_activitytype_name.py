# Generated by Django 3.2.10 on 2022-04-11 01:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0027_rename_activity_type_activity_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='activitytype',
            old_name='type',
            new_name='name',
        ),
    ]
