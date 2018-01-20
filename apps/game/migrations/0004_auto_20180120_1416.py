# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-20 10:46
from __future__ import unicode_literals

import apps.game.models.competition
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20180111_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamsubmission',
            name='status',
            field=models.CharField(choices=[('uploading', 'Uploading'), ('uploaded', 'Uploaded'), ('compiling', 'Compiling'), ('compiled', 'Compiled')], default='uploading', max_length=128),
        ),
        migrations.AlterField(
            model_name='match',
            name='log',
            field=models.FileField(blank=True, null=True, upload_to=apps.game.models.competition.get_log_file_directory),
        ),
        migrations.AlterField(
            model_name='teamsubmission',
            name='language',
            field=models.CharField(choices=[('c++', 'C++'), ('java', 'Java'), ('python2', 'Python 2'), ('python3', 'Python 3')], max_length=128),
        ),
    ]