# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-09 02:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0013_professional_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professional',
            name='avatar',
        ),
    ]
