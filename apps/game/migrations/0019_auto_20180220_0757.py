# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-20 07:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0018_auto_20180214_0142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='match',
            name='infra_match_message',
        ),
        migrations.RemoveField(
            model_name='match',
            name='infra_token',
        ),
        migrations.RemoveField(
            model_name='match',
            name='log',
        ),
    ]