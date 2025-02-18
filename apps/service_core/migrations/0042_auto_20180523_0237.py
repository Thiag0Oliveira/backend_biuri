# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-05-23 02:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0041_attendanceprofessionalconfirmation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='services',
            field=models.ManyToManyField(through='service_core.AttendanceService', to='service_core.Service'),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], db_index=True, default='draft', max_length=100, no_check_for_status=True),
        ),
        migrations.AlterField(
            model_name='attendanceservice',
            name='attendance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_relation', related_query_name='attendance_relation', to='service_core.Attendance'),
        ),
    ]
