# Generated by Django 3.2.3 on 2021-08-17 02:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0019_auto_20210817_0214'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='start_lat',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='start_lng',
        ),
    ]