# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-02-05 15:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0079_contract_contractclause'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='title',
            field=models.CharField(default='', max_length=200, verbose_name='Modelo de Contrato'),
        ),
    ]
