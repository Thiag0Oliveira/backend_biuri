# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-01-03 16:51
from __future__ import unicode_literals

from django.db import migrations
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('company_sale', '0009_auto_20190103_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='canceled_date',
            field=model_utils.fields.MonitorField(blank=True, default=None, monitor='status', null=True, when=set(['canceled'])),
        ),
        migrations.AddField(
            model_name='sale',
            name='completed_date',
            field=model_utils.fields.MonitorField(blank=True, default=None, monitor='status', null=True, when=set(['completed'])),
        ),
        migrations.AddField(
            model_name='sale',
            name='waiting_approval_date',
            field=model_utils.fields.MonitorField(blank=True, default=None, monitor='status', null=True, when=set(['waiting_approval'])),
        ),
        migrations.AddField(
            model_name='sale',
            name='waiting_payment_date',
            field=model_utils.fields.MonitorField(blank=True, default=None, monitor='status', null=True, when=set(['waiting_payment'])),
        ),
        migrations.AlterField(
            model_name='sale',
            name='status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], db_index=True, default='draft', max_length=100, no_check_for_status=True),
        ),
        migrations.DeleteModel(
            name='SaleStatus',
        ),
    ]
