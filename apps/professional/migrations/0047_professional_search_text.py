# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-09-21 16:43
from __future__ import unicode_literals

from django.db import migrations, models
from ..models import Professional


class Migration(migrations.Migration):
    dependencies = [
        ('professional', '0045_auto_20180809_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='search_text',
            field=models.CharField(db_index=True, default='', max_length=200),
        )
    ]