# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-15 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0004_auto_20171113_1909'),
        ('lead_captation', '0002_auto_20171114_0800'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicallead',
            name='category',
        ),
        migrations.RemoveField(
            model_name='lead',
            name='category',
        ),
        migrations.AddField(
            model_name='lead',
            name='category',
            field=models.ManyToManyField(to='service_core.Category'),
        ),
    ]