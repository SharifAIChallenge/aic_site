# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-02-08 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0027_map_time_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='singlematch',
            name='status',
            field=models.CharField(choices=[('running', 'Running'), ('failed', 'Failed'), ('done', 'Done'), ('waiting', 'Waiting'), ('waitacc', 'Wating to accept')], default='waiting', max_length=128),
        ),
    ]
