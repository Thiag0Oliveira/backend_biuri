# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-09 02:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_auto_20180108_2234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='avatar_image',
        ),
    ]