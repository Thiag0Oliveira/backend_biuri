# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-11 15:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0028_auto_20190110_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salevouchergenerator',
            name='final_date',
            field=models.DateTimeField(verbose_name='Data final'),
        ),
        migrations.AlterField(
            model_name='salevouchergenerator',
            name='initial_date',
            field=models.DateTimeField(verbose_name='Data inicial'),
        ),
    ]