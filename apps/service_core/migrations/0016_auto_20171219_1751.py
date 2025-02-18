# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-19 20:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0015_attendance_waiting_customer_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='PricingCriterion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Pricing Criterion',
            },
        ),
        migrations.AddField(
            model_name='attendance',
            name='observation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_administrate_tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='attendanceservice',
            name='duration',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendanceservice',
            name='is_in_attendance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendanceservice',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
            preserve_default=False,
        ),
    ]
