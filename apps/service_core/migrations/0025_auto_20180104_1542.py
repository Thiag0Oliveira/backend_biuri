# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-04 18:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0024_auto_20180104_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendance',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendance',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='canceled_date',
            field=model_utils.fields.MonitorField(blank=True, default=None, monitor='status', null=True, when=set(['canceled_by_customer', 'canceled_by_professional'])),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='completed_date',
            field=model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['completed'])),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='confirmated_date',
            field=model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['confirmated'])),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='expired_date',
            field=model_utils.fields.MonitorField(blank=True, default=None, monitor='status', null=True, when=set(['expired'])),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='in_attendance_date',
            field=model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['in_attendance'])),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='on_transfer_date',
            field=model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['on_transfer'])),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='waiting_confirmation_date',
            field=model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['waiting_confirmation'])),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='waiting_customer_date',
            field=model_utils.fields.MonitorField(default=None, monitor='status', null=True, when=set(['waiting_customer'])),
        ),
    ]
