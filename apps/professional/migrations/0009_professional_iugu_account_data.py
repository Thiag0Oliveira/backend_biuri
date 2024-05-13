# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-03 20:57
from __future__ import unicode_literals

import apps.common.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0008_auto_20171227_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='iugu_account_data',
            field=apps.common.fields.JSONField(default=dict, verbose_name='iugo account data'),
        ),
    ]
