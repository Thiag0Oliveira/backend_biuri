# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-24 22:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0023_evaluationtype_picture_gray'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationtype',
            name='description_color',
            field=models.CharField(default='#FABA2C', max_length=10),
        ),
    ]