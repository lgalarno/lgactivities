# Generated by Django 3.2.3 on 2021-07-21 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_alter_stravaprofile_avatar_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stravaprofile',
            name='avatar_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]