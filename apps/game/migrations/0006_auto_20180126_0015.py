# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-25 20:45
from __future__ import unicode_literals

import apps.game.models.competition
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20180124_2151'),
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
            field=models.FileField(blank=True, null=True, upload_to=apps.game.models.competition.get_log_file_directory),
        ),
        migrations.AlterField(
            model_name='teamsubmission',
            name='status',
            field=models.CharField(choices=[('uploading', 'Uploading'), ('uploaded', 'Uploaded'), ('compiling', 'Compiling'), ('compiled', 'Compiled'), ('failed', 'Failed')], default='uploading', max_length=128),
        ),
    ]