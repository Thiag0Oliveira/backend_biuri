# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-01 22:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0030_attendance_pricing_criterion_option'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Address'),
        ),
    ]
