# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-28 17:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0049_auto_20180720_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.Customer'),
        ),
    ]