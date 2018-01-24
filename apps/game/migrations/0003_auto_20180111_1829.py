# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-11 18:29
from __future__ import unicode_literals

import apps.game.models.competition
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20180104_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='infra_match_message',
            field=models.CharField(blank=True, max_length=1023, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='infra_token',
            field=models.CharField(blank=True, max_length=256, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='match',
            name='log',
            field=models.FileField(default='', upload_to=apps.game.models.competition.get_log_file_directory),
            preserve_default=False,
        ),
    ]