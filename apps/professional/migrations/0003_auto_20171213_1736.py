# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-13 20:36
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0002_serviceprofessional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoriteprofessional',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='customer.Customer'),
        ),
        migrations.AlterField(
            model_name='favoriteprofessional',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='professional.Professional'),
        ),
        migrations.AlterField(
            model_name='professional',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='professional.Professional'),
        ),
    ]
