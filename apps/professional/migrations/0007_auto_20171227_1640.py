# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-27 19:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0018_auto_20171227_1534'),
        ('professional', '0006_schedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=40)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='badges/')),
            ],
            options={
                'verbose_name': 'Badges',
            },
        ),
        migrations.CreateModel(
            name='ProfessionalBadge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='professional.Badge')),
            ],
            options={
                'verbose_name': 'Badges',
            },
        ),
        migrations.CreateModel(
            name='ProfessionalEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('rating', models.PositiveIntegerField()),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='service_core.Attendance')),
            ],
            options={
                'verbose_name': 'Professional Evaluation',
            },
        ),
        migrations.AddField(
            model_name='professional',
            name='attendance_cancelation_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='professional',
            name='attendance_completed_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='professional',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='professional',
            name='rating',
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AddField(
            model_name='professionalevaluation',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='professional.Professional'),
        ),
        migrations.AddField(
            model_name='professionalbadge',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='professional.Professional'),
        ),
        migrations.AddField(
            model_name='professional',
            name='badges',
            field=models.ManyToManyField(through='professional.ProfessionalBadge', to='professional.Badge'),
        ),
    ]
