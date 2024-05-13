# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-04-11 13:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0034_auto_20180409_1643'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favoriteprofessional',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='professional_favorites', to='customer.Customer'),
        ),
        migrations.AlterField(
            model_name='favoriteprofessional',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='customer_favorites', to='professional.Professional'),
        ),
    ]