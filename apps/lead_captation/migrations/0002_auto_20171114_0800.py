# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-14 11:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lead_captation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Address'),
        ),
    ]
