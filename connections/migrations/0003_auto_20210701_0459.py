# Generated by Django 3.2.3 on 2021-07-01 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('connections', '0002_auto_20210701_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='expires_at',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='token',
            name='expires_in',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]