# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-22 00:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_captation', '0014_auto_20171121_1817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='category',
            field=models.ManyToManyField(null=True, to='service_core.Category'),
        ),
    ]
