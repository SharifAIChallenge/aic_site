# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-02-08 18:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0029_auto_20190208_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='map',
            name='verified',
            field=models.NullBooleanField(),
        ),
    ]
