# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-07-20 08:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('witio', '0002_auto_20160717_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.RegisteredUser'),
        ),
    ]