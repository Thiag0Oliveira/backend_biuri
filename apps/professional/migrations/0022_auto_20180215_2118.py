# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-16 00:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0021_auto_20180215_2116'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EvaluationTypes',
            new_name='EvaluationType',
        ),
        migrations.AlterModelOptions(
            name='evaluationtype',
            options={'verbose_name': 'EvaluationType'},
        ),
    ]
