# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-05-20 16:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0055_auto_20190125_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricingcriterionoptions',
            name='pricing_criterion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='service_core.PricingCriterion'),
        ),
    ]
