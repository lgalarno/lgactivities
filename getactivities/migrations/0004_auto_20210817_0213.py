# Generated by Django 3.2.3 on 2021-08-17 02:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getactivities', '0003_alter_getactivitiestask_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='getactivitiestask',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='getactivitiestask',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2021, 8, 17, 2, 11, 39, 735212)),
            preserve_default=False,
        ),
    ]