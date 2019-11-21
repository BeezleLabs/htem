# Generated by Django 2.0.6 on 2018-07-02 23:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event_manager', '0016_auto_20180701_1912'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True)),
                ('text', models.TextField(blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('conference', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(blank=True)),
                ('answer', models.TextField(blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('conference', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default='2018-01-01T01:00:00-00:00')),
                ('text', models.TextField(blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('conference', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
    ]
