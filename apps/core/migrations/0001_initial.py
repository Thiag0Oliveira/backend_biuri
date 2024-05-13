# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-03 22:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endereco', models.CharField(max_length=300)),
                ('numero', models.CharField(blank=True, max_length=20, null=True)),
                ('complemento', models.CharField(blank=True, max_length=100, null=True)),
                ('ponto_referencia', models.CharField(blank=True, max_length=100, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=12, max_digits=14, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=12, max_digits=14, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=12, max_digits=14, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=12, max_digits=14, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Neighborhood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.City')),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('cep', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('place_type', models.CharField(blank=True, max_length=80, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=12, max_digits=14, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=12, max_digits=14, null=True)),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='core.City')),
                ('neighborhood', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='core.Neighborhood')),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='city',
            name='state',
            field=models.ForeignKey(blank=True, max_length=2, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.State'),
        ),
        migrations.AddField(
            model_name='address',
            name='cidade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.City'),
        ),
        migrations.AddField(
            model_name='address',
            name='neighborhood',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.Neighborhood'),
        ),
        migrations.AddField(
            model_name='address',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Place'),
        ),
        migrations.AddField(
            model_name='address',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.State'),
        ),
    ]
