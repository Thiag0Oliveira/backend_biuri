# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-02-05 13:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0058_attendance_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='type',
            field=models.CharField(choices=[('has_preference', 'Agendando Diretamente'), ('dont_has_preference', 'Peça Já')], default='dont_has_preference', max_length=20),
        ),
    ]
