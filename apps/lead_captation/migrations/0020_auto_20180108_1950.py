# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-08 22:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_captation', '0019_auto_20180103_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='category',
            field=models.ManyToManyField(to='service_core.Category'),
        ),
    ]