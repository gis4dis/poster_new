# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-28 21:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('importing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReadonlyProviderLog',
            fields=[
            ],
            options={
                'indexes': [],
                'proxy': True,
            },
            bases=('importing.providerlog',),
        ),
        migrations.AlterField(
            model_name='providerlog',
            name='content_type',
            field=models.CharField(default='application/txt', max_length=32),
        ),
        migrations.AlterField(
            model_name='providerlog',
            name='is_valid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='providerlog',
            name='received_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
