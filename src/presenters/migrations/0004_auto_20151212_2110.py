# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('presenters', '0003_auto_20151211_1838'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform',
            name='login_param',
            field=models.TextField(),
        ),
    ]
