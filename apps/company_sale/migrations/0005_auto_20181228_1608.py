# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-28 16:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0004_auto_20181228_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Address'),
        ),
    ]