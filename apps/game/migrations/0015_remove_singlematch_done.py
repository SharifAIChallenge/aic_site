# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-06 11:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0014_challenge_is_submission_open'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singlematch',
            name='done',
        ),
    ]
