# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-12 14:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_state_uf'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='cod_ibge',
            field=models.IntegerField(null=True),
        ),
    ]