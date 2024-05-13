# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-05-20 16:47
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0083_merge_20190215_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professional',
            name='attendance_percent',
            field=models.PositiveIntegerField(default=70, validators=[django.core.validators.MaxValueValidator(85), django.core.validators.MinValueValidator(60)], verbose_name='Percentual do Profissional'),
        ),
        migrations.AlterField(
            model_name='professional',
            name='executive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='professional.Executive', verbose_name='Executivo'),
        ),
        migrations.AlterField(
            model_name='professional',
            name='is_test',
            field=models.BooleanField(default=False, verbose_name='Profissional de Teste'),
        ),
        migrations.AlterField(
            model_name='professional',
            name='professional_enabled',
            field=models.BooleanField(default=False, verbose_name='Profissional Liberado'),
        ),
    ]
