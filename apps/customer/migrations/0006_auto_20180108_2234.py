# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-09 01:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0005_customer_avatar'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='avatar',
            new_name='avatar_image',
        ),
    ]
