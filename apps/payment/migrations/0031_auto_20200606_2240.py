# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-06-06 22:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0030_auto_20200113_2355'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pendente'), ('processing', 'Processando'), ('accepted', 'Concluída'), ('rejected', 'Rejeitada'), ('canceled', 'Cancelado')], default='pending', max_length=10),
        ),
    ]
