# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-10 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0045_auto_20180809_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='iugu_account_id',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]
