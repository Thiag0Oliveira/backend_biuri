# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-28 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_captation', '0017_remove_profissionallead_codigo_executivo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='category',
            field=models.ManyToManyField(to='service_core.Category'),
        ),
    ]
