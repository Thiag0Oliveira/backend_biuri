# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-05-20 16:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0084_auto_20190520_1647'),
        ('lead_captation', '0030_merge_20190215_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicallead',
            name='executive',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='professional.Executive'),
        ),
        migrations.AddField(
            model_name='lead',
            name='executive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='professional.Executive'),
        ),
    ]