# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-22 01:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cog', '0004_auto_20160106_0812'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='shared',
            field=models.BooleanField(default=True),
        ),
    ]