# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-28 17:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20180828_1736'),
        ('service_core', '0050_auto_20180828_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='neighborhood',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Neighborhood'),
        ),
    ]