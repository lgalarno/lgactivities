# Generated by Django 3.2.10 on 2022-03-29 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('getactivities', '0013_auto_20210919_0438'),
    ]

    operations = [
        migrations.RenameField(
            model_name='syncactivitiestask',
            old_name='end_date',
            new_name='to_date',
        ),
        migrations.AddField(
            model_name='syncactivitiestask',
            name='from_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
