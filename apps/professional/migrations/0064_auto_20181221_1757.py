# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-21 17:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0063_auto_20181221_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionaldocument',
            name='document_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='tipo_documento', to='professional.DocumentType'),
        ),
    ]
