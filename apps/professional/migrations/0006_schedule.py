# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-27 19:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0005_auto_20171227_1602'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('daily_time_begin', models.TimeField()),
                ('daily_time_end', models.TimeField()),
                ('daily_date', models.DateField()),
                ('professional', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='professional.Professional')),
            ],
            options={
                'verbose_name': 'Schedule',
            },
        ),
    ]
