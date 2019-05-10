# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cog', '0002_auto_20150706_1045'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='nodesWidgetEnabled',
            field=models.BooleanField(default=False, help_text=b'Enable federated nodes widget ?'),
        ),
    ]
