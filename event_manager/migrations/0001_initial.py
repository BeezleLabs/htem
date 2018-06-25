# Generated by Django 2.0 on 2018-02-10 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=2048)),
                ('description', models.TextField()),
                ('code', models.CharField(max_length=16)),
                ('link', models.URLField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_id', models.CharField(max_length=32)),
                ('title', models.CharField(max_length=2048)),
                ('description', models.TextField()),
                ('link', models.URLField()),
                ('exploit', models.BooleanField(default=False)),
                ('tool', models.BooleanField(default=False)),
                ('demo', models.BooleanField(default=False)),
                ('includes', models.CharField(max_length=256)),
                ('dctv_channel', models.CharField(max_length=32)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=256)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(max_length=1024)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sptitle', models.CharField(max_length=2048)),
                ('who', models.CharField(max_length=2048)),
                ('twitter', models.CharField(max_length=512)),
                ('link', models.URLField()),
                ('bio', models.TextField()),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=1024)),
                ('description', models.TextField()),
                ('link', models.URLField(max_length=2048)),
                ('partner', models.BooleanField(default=False)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager.Conference')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager.EventType'),
        ),
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='event_manager.Location'),
        ),
        migrations.AddField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(to='event_manager.Speaker'),
        ),
    ]
