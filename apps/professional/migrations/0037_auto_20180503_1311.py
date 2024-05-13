# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-03 13:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0036_professionalscheduledefault'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionalscheduledefault',
            name='day_of_week',
            field=models.CharField(choices=[('0', 'SEGUNDA-FEIRA'), ('1', 'TERÇA-FEIRA'), ('2', 'QUARTA-FEIRA'), ('3', 'QUINTA-FEIRA'), ('4', 'SEXTA-FEIRA'), ('5', 'SÁBADO'), ('6', 'DOMINGO')], max_length=20),
        ),
    ]