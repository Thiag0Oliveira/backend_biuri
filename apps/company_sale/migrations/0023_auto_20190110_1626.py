# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-10 16:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0022_auto_20190110_1623'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'permissions': (('list_sale', 'Can view list of sales'), ('edit_seller', 'Can edit seller'), ('edit_executive', 'Can edit executive')), 'verbose_name': 'Sale'},
        ),
    ]
