# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-15 13:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lead_captation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicallead',
            name='type',
            field=models.CharField(choices=[('', 'Selecione categoria'), ('Profissional', 'Profissional'), ('Executive', 'Executive')], max_length=20),
        ),
        migrations.AlterField(
            model_name='lead',
            name='type',
            field=models.CharField(choices=[('', 'Selecione categoria'), ('Profissional', 'Profissional'), ('Executive', 'Executive')], max_length=20),
        ),
    ]
