# Generated by Django 3.2.3 on 2021-08-17 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0021_alter_segment_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='segment',
            name='start_lat',
        ),
        migrations.RemoveField(
            model_name='segment',
            name='start_lng',
        ),
    ]
