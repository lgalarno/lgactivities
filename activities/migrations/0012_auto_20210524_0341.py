# Generated by Django 3.2.3 on 2021-05-24 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0011_auto_20210524_0301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segment',
            name='kom',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='segment',
            name='qom',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
