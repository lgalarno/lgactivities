# Generated by Django 3.2.3 on 2021-08-13 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getactivities', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getactivitiestask',
            name='frequency',
            field=models.IntegerField(choices=[('Daily', 1), ('Weekly', 7), ('Monthly', 30)], default='Weekly'),
        ),
    ]