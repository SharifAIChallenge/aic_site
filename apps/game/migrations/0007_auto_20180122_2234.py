# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-22 19:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_merge_20180120_2352'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name_plural': 'matches'},
        ),
        migrations.AlterModelOptions(
            name='teamparticipateschallenge',
            options={'verbose_name_plural': 'Team Participates In Challenges'},
        ),
        migrations.AlterField(
            model_name='teamsubmission',
            name='language',
            field=models.CharField(choices=[('c++', 'C++'), ('java', 'Java'), ('python2', 'Python 2'), ('python3', 'Python 3')], default='java', max_length=128),
        ),
    ]
