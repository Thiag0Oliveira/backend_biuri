# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-12 11:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0008_customer_avatar_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='celphone',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
    ]
