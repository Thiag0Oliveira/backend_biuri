# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-11-29 15:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0051_attendance_neighborhood'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='total_interest',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]