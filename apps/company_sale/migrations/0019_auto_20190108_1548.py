# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-08 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0018_auto_20190107_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='salevouchergenerator',
            name='final_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salevouchergenerator',
            name='initial_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
