# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-31 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20180103_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='address',
            field=models.CharField(max_length=300, verbose_name='Endereço'),
        ),
        migrations.AlterField(
            model_name='address',
            name='complement',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Complemento'),
        ),
        migrations.AlterField(
            model_name='address',
            name='number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='address',
            name='reference_point',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Pont de referência'),
        ),
    ]
