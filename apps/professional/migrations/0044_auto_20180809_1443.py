# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-09 14:43
from __future__ import unicode_literals

import apps.common.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0043_professional_instagram_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professional',
            name='iugu_account_data',
            field=apps.common.fields.JSONField(default=dict, verbose_name='iugu account data'),
        ),
    ]
