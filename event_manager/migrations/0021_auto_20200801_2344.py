# Generated by Django 2.2.7 on 2020-08-01 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_manager', '0020_auto_20200731_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventtype',
            name='discord_url',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AddField(
            model_name='eventtype',
            name='subforum_url',
            field=models.CharField(default='', max_length=256),
        ),
        migrations.AlterField(
            model_name='eventtype',
            name='tags',
            field=models.CharField(default='', max_length=256),
        ),
    ]
