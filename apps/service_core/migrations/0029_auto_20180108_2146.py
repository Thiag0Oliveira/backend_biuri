# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-09 00:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0028_auto_20180108_2027'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalservice',
            name='picture',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='services/'),
        ),
    ]
