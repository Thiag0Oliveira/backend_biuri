# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-12 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_state_cod_ibge'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='cod_ibge',
            field=models.IntegerField(null=True),
        ),
    ]
