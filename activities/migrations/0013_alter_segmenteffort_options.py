# Generated by Django 3.2.3 on 2021-05-31 04:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0012_auto_20210524_0341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='segmenteffort',
            options={'ordering': ['start_date_local']},
        ),
    ]
