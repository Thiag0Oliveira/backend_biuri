# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-03-08 17:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service_core', '0033_auto_20180208_2305'),
        ('professional', '0025_professional_bank_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfessionalCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='service_core.Category', verbose_name='Cidade')),
            ],
        ),
        migrations.AlterField(
            model_name='professional',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='professional_principal', to='service_core.Category', verbose_name='Área Principal'),
        ),
        migrations.AddField(
            model_name='professionalcategory',
            name='professional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='professional.Professional'),
        ),
        migrations.AddField(
            model_name='professionalcategory',
            name='services',
            field=models.ManyToManyField(to='service_core.Service', verbose_name='Serviços'),
        ),
    ]