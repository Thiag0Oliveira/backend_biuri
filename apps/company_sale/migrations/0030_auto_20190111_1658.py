# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-11 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0029_auto_20190111_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salevouchergenerator',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='service_voucher', to='service_core.Service', verbose_name='Serviço'),
        ),
    ]