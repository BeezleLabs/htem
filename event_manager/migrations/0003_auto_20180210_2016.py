# Generated by Django 2.0 on 2018-02-10 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_manager', '0002_auto_20180210_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]
