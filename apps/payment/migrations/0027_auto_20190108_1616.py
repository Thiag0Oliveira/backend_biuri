# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-08 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0026_auto_20190108_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voucher',
            name='code',
            field=models.SlugField(auto_created=True, blank=True, max_length=20, unique=True),
        ),
    ]
