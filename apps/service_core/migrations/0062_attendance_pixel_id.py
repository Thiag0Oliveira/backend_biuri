# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-05-17 18:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0061_auto_20200218_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='pixel_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]
