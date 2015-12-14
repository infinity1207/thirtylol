# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('url', models.CharField(max_length=50)),
                ('intro', models.TextField()),
                ('logo', models.ImageField(upload_to=b'platform_logos', blank=True)),
                ('login_param', models.CharField(max_length=255)),
                ('fetch_status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Presenter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_in_platform', models.IntegerField(default=0)),
                ('nickname', models.CharField(max_length=50)),
                ('introduce', models.TextField()),
                ('room_url', models.CharField(max_length=255, blank=True)),
                ('gender', models.CharField(default=b'M', max_length=1, choices=[(b'F', b'Female'), (b'M', b'Male')])),
                ('avatar_url', models.CharField(max_length=255, blank=True)),
                ('join_date', models.DateField(auto_now_add=True)),
                ('invalid', models.BooleanField(default=True)),
                ('platform', models.ForeignKey(to='presenters.Platform')),
            ],
        ),
        migrations.CreateModel(
            name='PresenterDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('showing', models.BooleanField(default=False)),
                ('room_title', models.CharField(max_length=255, blank=True)),
                ('duration', models.IntegerField(default=0)),
                ('audience_count', models.IntegerField(default=0)),
                ('last_show_end', models.DateTimeField(null=True, blank=True)),
                ('presenter', models.OneToOneField(to='presenters.Presenter')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='presenter',
            name='tag',
            field=models.ManyToManyField(to='presenters.Tag', blank=True),
        ),
    ]
