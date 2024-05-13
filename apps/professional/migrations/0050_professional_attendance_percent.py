# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-12-11 15:27
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0049_auto_20181113_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='attendance_percent',
            field=models.PositiveIntegerField(default=70, validators=[django.core.validators.MaxValueValidator(85), django.core.validators.MinValueValidator(60)]),
        ),
    ]