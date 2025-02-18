# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-03 17:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0053_attendance_splits_number'),
        ('company_sale', '0011_auto_20190103_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleVoucherGenerator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('quantity', models.PositiveIntegerField(blank=True, default=0, verbose_name='Quantidade')),
                ('value', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=12, verbose_name='Valor')),
                ('observation', models.TextField(blank=True, max_length=500, null=True, verbose_name='Observações')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sale_generator', to='company_sale.Sale', verbose_name='Venda')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_voucher', to='service_core.Service', verbose_name='Serviço')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='salevouchertemplate',
            name='service',
        ),
        migrations.DeleteModel(
            name='SaleVoucherTemplate',
        ),
    ]
