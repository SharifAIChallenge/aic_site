# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-03-06 06:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20190208_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='fullname_eng',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Full Name in English'),
        ),
    ]