# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-11 17:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0074_auto_20190111_1738'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='executive',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='executive', to='professional.Executive', verbose_name='Executivo'),
            preserve_default=False,
        ),
    ]
