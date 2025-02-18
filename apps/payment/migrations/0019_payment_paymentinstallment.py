# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-19 16:53
from __future__ import unicode_literals

import apps.common.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0053_attendance_splits_number'),
        ('payment', '0018_auto_20181211_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('invoice_id', models.CharField(max_length=40, unique=True)),
                ('information_data', apps.common.fields.JSONField(default=dict, verbose_name='information_data')),
                ('attendance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='service_core.Attendance')),
            ],
            options={
                'verbose_name': 'Transaction',
            },
        ),
        migrations.CreateModel(
            name='PaymentInstallment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('installment_id', models.PositiveIntegerField(unique=True)),
                ('installment_data', apps.common.fields.JSONField(default=dict, verbose_name='information_data')),
                ('payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='payment.Payment')),
            ],
            options={
                'verbose_name': 'Transaction',
            },
        ),
    ]
