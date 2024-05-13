# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-27 15:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0020_paymentinstallment_is_received'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={},
        ),
        migrations.AlterModelOptions(
            name='paymentinstallment',
            options={},
        ),
        migrations.AlterField(
            model_name='payment',
            name='attendance',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='payments', to='service_core.Attendance'),
        ),
    ]
