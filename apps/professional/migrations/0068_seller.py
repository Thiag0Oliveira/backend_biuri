# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2018-12-27 17:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_useraddress_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0021_auto_20181227_1644'),
        ('professional', '0067_auto_20181227_1644'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('cellphone', models.CharField(blank=True, max_length=11, null=True, verbose_name='Telefone')),
                ('observation', models.CharField(blank=True, max_length=2000, null=True)),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='common.Address')),
                ('bank_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.BankAccount')),
                ('executive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='executive', to='professional.Executive', verbose_name='Executivo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='seller', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Vendedor',
            },
        ),
    ]
