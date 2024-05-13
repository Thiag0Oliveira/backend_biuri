# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-08-09 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0013_auto_20180717_1326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='account_type',
            field=models.CharField(choices=[('Corrente', 'CONTA CORRENTE'), ('Poupança', 'POUPANÇA')], max_length=10, verbose_name='Tipo da conta'),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='bank',
            field=models.CharField(choices=[('Banco do Brasil', '001 - BANCO DO BRASIL S.A.'), ('Santander', '033 - BANCO SANTANDER (BRASIL) S.A.'), ('Bradesco', '036 - BANCO BRADESCO BBI S.A.'), ('Caixa Econômica', '104 - CAIXA ECONOMICA FEDERAL'), ('Itaú', '041 - BANCO ITAÚ S.A.'), ('Sicredi', '748 - BANCO COOPERATIVO SICREDI S.A.'), ('Sicoob', '756 - BANCO COOPERATIVO DO BRASIL S.A. - BANCOOB')], max_length=100, verbose_name='Banco'),
        ),
    ]
