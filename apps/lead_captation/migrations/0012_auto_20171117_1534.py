# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-17 18:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lead_captation', '0011_auto_20171116_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicallead',
            name='type',
            field=models.CharField(blank=True, choices=[('Profissional', 'Profissional'), ('Executive', 'Executive')], max_length=20),
        ),
        migrations.AlterField(
            model_name='lead',
            name='type',
            field=models.CharField(blank=True, choices=[('Profissional', 'Profissional'), ('Executive', 'Executive')], max_length=20),
        ),
    ]
