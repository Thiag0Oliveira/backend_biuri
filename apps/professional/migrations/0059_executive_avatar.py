# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-20 16:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0058_auto_20181220_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='executive',
            name='avatar',
            field=models.ImageField(blank=True, default='professional/avatar/default.png', upload_to='executive/avatar/'),
        ),
    ]