# Generated by Django 3.2.3 on 2021-07-22 04:35

from django.db import migrations, models
import profiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_alter_stravaprofile_avatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='stravaprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=profiles.models.upload_location),
        ),
    ]
