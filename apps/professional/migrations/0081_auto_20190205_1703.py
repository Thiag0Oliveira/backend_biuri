# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-02-05 17:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0080_auto_20190205_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractclause',
            name='text',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Texto'),
        ),
    ]