# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-10 16:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0038_auto_20180507_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceprofessional',
            name='average_time',
            field=models.PositiveIntegerField(default=0, verbose_name='Tempo Médio em minutos'),
        ),
        migrations.AlterField(
            model_name='serviceprofessional',
            name='maximum_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='Preço Máximo'),
        ),
        migrations.AlterField(
            model_name='serviceprofessional',
            name='minimum_price',
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Preço (R$)'),
        ),
        migrations.AlterField(
            model_name='serviceprofessional',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service_core.Service', verbose_name='Serviço'),
        ),
    ]
