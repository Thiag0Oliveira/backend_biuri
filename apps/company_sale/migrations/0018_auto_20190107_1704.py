# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-07 17:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0017_auto_20190107_1529'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'permissions': (('can_edit_company', 'can edit company'),), 'verbose_name': 'Company'},
        ),
    ]
