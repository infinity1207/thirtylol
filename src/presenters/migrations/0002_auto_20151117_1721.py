# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('presenters', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShowHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('stop', models.DateTimeField()),
                ('duration', models.IntegerField()),
                ('presenter', models.ForeignKey(to='presenters.Presenter')),
            ],
        ),
        migrations.RemoveField(
            model_name='presenterdetail',
            name='duration',
        ),
        migrations.AddField(
            model_name='presenterdetail',
            name='start',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
