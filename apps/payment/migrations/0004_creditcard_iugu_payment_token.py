# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-03 21:41
from __future__ import unicode_literals

import apps.common.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20171213_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditcard',
            name='iugu_payment_token',
            field=apps.common.fields.JSONField(default=dict, verbose_name='iugu payment token'),
        ),
    ]
