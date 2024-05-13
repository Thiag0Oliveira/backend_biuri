# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-09-17 12:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professional', '0091_professionalpicture'),
        ('payment', '0032_auto_20200609_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='voucher',
            name='executive',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='professional.Executive'),
        ),
        migrations.AddField(
            model_name='voucher',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='Ativo'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='code',
            field=models.SlugField(auto_created=True, blank=True, max_length=20, unique=True, verbose_name='Código Promocional'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='discount',
            field=models.IntegerField(default=0, verbose_name='Desconto'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='discount_type',
            field=models.CharField(choices=[('percent', 'Percentual'), ('value', 'Valor Exato')], db_index=True, default='percent', max_length=20, verbose_name='Tipo de Desconto'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='final_date',
            field=models.DateTimeField(verbose_name='Data Final'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='initial_date',
            field=models.DateTimeField(verbose_name='Data Inicial'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Quantidade'),
        ),
        migrations.AlterField(
            model_name='voucher',
            name='validation_type',
            field=models.CharField(choices=[('one_use', 'Uso Único'), ('multiple_use', 'Usos Múltiplos')], db_index=True, default='one_use', max_length=20, verbose_name='Tipo de Validação'),
        ),
    ]
