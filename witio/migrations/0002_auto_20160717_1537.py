# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-17 15:37
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('witio', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='wit_context',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]