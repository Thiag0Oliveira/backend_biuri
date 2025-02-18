# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-08 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0023_auto_20190103_1727'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='observation',
            field=models.TextField(blank=True, max_length=500, null=True, verbose_name='Observações'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='validation_type',
            field=models.CharField(choices=[('one_use', 'one_use'), ('multiple_use', 'multiple_use')], db_index=True, default='one_use', max_length=20),
        ),
    ]
