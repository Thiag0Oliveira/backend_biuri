# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-07 15:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0071_seller_commission_percent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seller',
            options={'permissions': (('can_edit_seller', 'can create and edit sellers'),), 'verbose_name': 'Vendedor'},
        ),
    ]