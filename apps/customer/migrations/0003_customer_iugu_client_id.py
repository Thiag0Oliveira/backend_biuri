# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-03 19:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_auto_20171213_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='iugu_client_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
