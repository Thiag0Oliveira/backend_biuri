# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-11 14:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0037_attendance_is_push_notificated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='is_push_notificated',
            field=models.BooleanField(default=False),
        ),
    ]
