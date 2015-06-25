# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='pnumber',
            field=models.IntegerField(default=1, help_text=b'Field to test new django migrations', blank=True),
        ),
    ]
