# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-01-17 11:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('intro', '0004_staff_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='color',
        ),
    ]