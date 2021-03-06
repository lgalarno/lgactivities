# Generated by Django 3.2.3 on 2021-05-24 03:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0010_auto_20210523_0552'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='kom',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='segment',
            name='qom',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='segment',
            name='updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='map',
            name='activity',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activities.activity'),
        ),
        migrations.AlterField(
            model_name='map',
            name='segment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='activities.segment'),
        ),
    ]
