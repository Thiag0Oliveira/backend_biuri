# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-17 19:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0008_auto_20171117_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalservice',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='service',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]