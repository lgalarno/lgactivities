# Generated by Django 3.2.10 on 2022-09-21 15:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('getactivities', '0001_initial'),
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncactivitiestask',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sync_activities_task', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='importactivitiestask',
            name='periodic_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_beat.periodictask'),
        ),
        migrations.AddField(
            model_name='importactivitiestask',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='import_activities_task', to=settings.AUTH_USER_MODEL),
        ),
    ]
