# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import shutil
import platform as pf
from django.utils import timezone

GENDER_CHOICES = (
    ('F', 'Female'),
    ('M', 'Male'),
)


class Platform(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=50)
    intro = models.TextField()
    logo = models.ImageField(upload_to='platform_logos', blank=True)

    login_param = models.TextField()
    fetch_status = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

# @receiver(post_save, sender=Platform)
def handle_platform_logo_filename(sender, instance, created, **kwargs):
    name = instance.logo.name
    if name:
        last_slash_pos = name.rindex('/')
        last_dot_pos = name.rindex('.')
        name_without_extension = name[last_slash_pos + 1:last_dot_pos]
        prefix = name[:last_slash_pos]
        extension = name[last_dot_pos + 1:]
        if name_without_extension == str(instance.id):
            return

        new_name = "%s/%s.%s" % (prefix, instance.id, extension)
        image_file_path = instance.logo.path
        if pf.system() == 'Windows':
            image_file_path_prefix = image_file_path[:image_file_path.rindex('\\')]
            new_image_file_path = "%s\\%s.%s" % (image_file_path_prefix, instance.id, extension)
        else:
            image_file_path_prefix = image_file_path[:image_file_path.rindex('/')]
            new_image_file_path = "%s/%s.%s" % (image_file_path_prefix, instance.id, extension)

        shutil.move(image_file_path, new_image_file_path)
        instance.logo.name = new_name
        instance.save()

class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Game(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

def get_default_game():
    return Game.objects.get_or_create(name=u"英雄联盟")[0].id

class Presenter(models.Model):
    game = models.ForeignKey('Game', default=get_default_game)
    platform = models.ForeignKey('Platform')
    id_in_platform = models.IntegerField(default=0)
    tag = models.ManyToManyField('Tag', blank=True)
    nickname = models.CharField(max_length=50)
    introduce = models.TextField()
    room_url = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    avatar_url = models.CharField(max_length=255, blank=True)

    join_date = models.DateField(auto_now_add=True)

    invalid = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nickname


class RecommendPresenter(object):
    platform = models.ForeignKey('Platform')
    nickname = models.CharField(max_length=50)
    introduce = models.TextField()
    approve = models.NullBooleanField()
    
    email = models.EmailField()

    def __unicode__(self):
        return self.nickname

        
class PresenterDetail(models.Model):
    presenter = models.OneToOneField('Presenter')

    showing = models.BooleanField(default=False)
    room_title = models.CharField(max_length=255, blank=True)
    audience_count = models.IntegerField(default=0)

    start = models.DateTimeField(null=True, blank=True)
    last_show_end = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.showing and not self.start:     # 开始直播
            self.start = timezone.now()
            self.last_show_end = None
        elif not self.showing and self.start:   # 结束直播
            self.auto_create_showhistory()
            self.last_show_end = timezone.now()
            self.start = None

        super(PresenterDetail, self).save()

    # 结束直播时记录本次直播信息
    def auto_create_showhistory(self):
        history = ShowHistory(presenter=self.presenter, start=self.start, stop=timezone.now())
        history.duration = (history.stop - history.start).total_seconds() / 60
        history.save()

    def __unicode__(self):
        return self.presenter.nickname

class ShowHistory(models.Model):
    presenter = models.ForeignKey('Presenter')

    start = models.DateTimeField()
    stop = models.DateTimeField()
    duration = models.IntegerField()


@receiver(post_save, sender=Presenter)
def auto_create_presenter_detail(sender, instance, created, *args, **kwargs):
    if not created:
        return
    detail = PresenterDetail(presenter=instance)
    detail.save()

# post_save.connect(auto_create_presenter_detail, sender=Presenter)
