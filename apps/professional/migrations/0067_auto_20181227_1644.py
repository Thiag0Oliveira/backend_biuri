# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-27 16:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0066_auto_20181226_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionaldocument',
            name='document_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='professional.DocumentType'),
        ),
        migrations.AlterField(
            model_name='professionaldocument',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='documentos', to='professional.Professional'),
        ),
    ]
