# Generated by Django 2.0 on 2018-06-17 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_manager', '0008_village'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(to='event_manager.Speaker'),
        ),
    ]
