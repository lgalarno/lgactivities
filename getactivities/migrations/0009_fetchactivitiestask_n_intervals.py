# Generated by Django 3.2.3 on 2021-08-24 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getactivities', '0008_auto_20210823_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='fetchactivitiestask',
            name='n_intervals',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
