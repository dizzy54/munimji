# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-25 15:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='registereduser',
            name='oauth_verifier',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='registereduser',
            name='resource_owner_key',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='registereduser',
            name='resource_owner_secret',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='registereduser',
            name='splitwise_key',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='registereduser',
            name='splitwise_secret',
            field=models.CharField(max_length=60, null=True),
        ),
    ]
