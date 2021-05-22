# Generated by Django 3.2 on 2021-05-16 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='Segment',
        ),
        migrations.AddField(
            model_name='map',
            name='segment',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='segment', to='activities.segment'),
        ),
        migrations.AlterField(
            model_name='map',
            name='activity',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='activity', to='activities.activity'),
        ),
    ]
