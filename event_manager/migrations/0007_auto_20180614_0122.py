# Generated by Django 2.0 on 2018-06-14 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event_manager', '0006_auto_20180614_0106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(null=True, to='event_manager.Speaker'),
        ),
    ]