# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-01 09:40
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20160726_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='registereduser',
            name='splitwise_friend_list',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True, verbose_name='list of splitwise friends'),
        ),
    ]
