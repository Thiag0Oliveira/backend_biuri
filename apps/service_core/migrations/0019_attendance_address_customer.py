# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-04 17:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20180103_1947'),
        ('service_core', '0018_auto_20171227_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='address_customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Address'),
        ),
    ]