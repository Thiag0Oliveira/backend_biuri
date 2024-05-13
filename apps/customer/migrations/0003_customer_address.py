# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-04 18:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20180103_1947'),
        ('customer', '0002_auto_20171213_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Address'),
        ),
    ]
