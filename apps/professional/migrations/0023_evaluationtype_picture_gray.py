# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-24 19:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0022_auto_20180215_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationtype',
            name='picture_gray',
            field=models.ImageField(blank=True, null=True, upload_to='evaluations/'),
        ),
    ]
