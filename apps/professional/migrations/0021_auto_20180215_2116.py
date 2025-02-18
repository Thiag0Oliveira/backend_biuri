# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-16 00:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0020_auto_20180201_1853'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=40)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='evaluations/')),
            ],
            options={
                'verbose_name': 'Badge',
            },
        ),
        migrations.AddField(
            model_name='professionalevaluation',
            name='evaluation_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='professional.EvaluationTypes'),
        ),
    ]
