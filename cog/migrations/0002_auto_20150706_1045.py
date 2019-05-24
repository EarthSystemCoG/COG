# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import models, migrations
import cog.models.dbutils


class Migration(migrations.Migration):

    dependencies = [
        ('cog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='project',
            field=cog.models.dbutils.UnsavedForeignKey(to='cog.Project'),
        ),
        migrations.AlterField(
            model_name='projecttab',
            name='project',
            field=cog.models.dbutils.UnsavedForeignKey(related_name='tabs', to='cog.Project'),
        ),
    ]
