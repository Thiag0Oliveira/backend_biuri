# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-03 17:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0012_auto_20190103_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salevouchergenerator',
            name='observation',
            field=models.TextField(blank=True, max_length=100, null=True, verbose_name='Observações'),
        ),
    ]