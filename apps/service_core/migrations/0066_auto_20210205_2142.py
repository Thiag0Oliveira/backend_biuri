# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2021-02-05 21:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0065_auto_20210115_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='flexible_date_end',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='flexible_date_start',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='flexible_discount',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]