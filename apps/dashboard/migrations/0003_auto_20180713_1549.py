# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-07-13 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_professionalvisualisation_attendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionalvisualisation',
            name='type',
            field=models.CharField(choices=[('profile', 'Perfil'), ('list', 'Listagem'), ('search', 'Busca')], max_length=10),
        ),
    ]
