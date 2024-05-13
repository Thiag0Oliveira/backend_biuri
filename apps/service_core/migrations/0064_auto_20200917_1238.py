# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-09-17 12:38
from __future__ import unicode_literals

from django.db import migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0063_auto_20200602_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], db_index=True, default='draft', max_length=100, no_check_for_status=True, verbose_name='Status'),
        ),
    ]
