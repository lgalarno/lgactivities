# Generated by Django 3.2.3 on 2021-08-17 02:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0017_activity_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='icon',
            field=models.CharField(blank=True, default='', max_length=127, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='name',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start_date_local',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start_lat',
            field=models.FloatField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start_lng',
            field=models.FloatField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='type',
            field=models.CharField(blank=True, default='', max_length=127, null=True),
        ),
    ]
