# Generated by Django 2.0 on 2018-06-28 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_manager', '0011_auto_20180623_0319'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='timezone',
            field=models.CharField(default='-06:00', max_length=10),
        ),
    ]