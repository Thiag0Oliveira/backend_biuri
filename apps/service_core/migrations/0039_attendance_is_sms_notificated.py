# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-11 15:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0038_auto_20180411_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='is_sms_notificated',
            field=models.BooleanField(default=True),
        ),
    ]
