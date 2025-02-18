# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-06-04 12:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0039_auto_20180510_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='send_sms',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='professional',
            name='gender',
            field=models.CharField(blank=True, choices=[('Masculino', 'Masculino'), ('Feminino', 'Feminino')], max_length=20, null=True, verbose_name='Sexo'),
        ),
    ]
