# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import presenters.models


class Migration(migrations.Migration):

    dependencies = [
        ('presenters', '0002_auto_20151117_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='presenter',
            name='game',
            field=models.ForeignKey(default=presenters.models.get_default_game, to='presenters.Game'),
        ),
    ]
