# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-07 15:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0015_auto_20190104_1601'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sale',
            options={'permissions': (('can_edit_sale', 'can edit sales'),), 'verbose_name': 'Sale'},
        ),
    ]