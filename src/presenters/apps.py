# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.models.fields.files import ImageFieldFile
from django.shortcuts import get_object_or_404
from django.http import Http404

def init_platform(sender, **kwargs):
    platforms = (
        {'name':u'斗鱼', 'url':'http://www.douyu.com/', 'intro':u'当下最火的游戏直播平台', 'logo':'platform_logos/1.jpg'},
        {'name':u'虎牙', 'url':'http://www.huya.com/', 'intro':u'YY旗下直播网站', 'logo':'platform_logos/2.jpg'},
        {'name':u'战旗', 'url':'http://www.zhanqi.com/', 'intro':u'浙报传媒与边锋网络共同打造', 'logo':'platform_logos/3.jpg'},
        {'name':u'龙珠', 'url':'http://www.longzhu.com/', 'intro':u'腾讯旗下', 'logo':'platform_logos/4.jpg'},
        {'name':u'熊猫', 'url':'http://www.panda.tv/', 'intro':u'王思聪投资', 'logo':'platform_logos/5.jpg'},
    )
    for item in platforms:
        my_module = sender.get_model('Platform')
        try:
            p = get_object_or_404(my_module, name=item['name'])
        except Http404:
            p = my_module()
            p.name = item['name']
            p.url = item['url']
            p.introduce = item['intro']
            p.logo = ImageFieldFile(p, p.logo, item['logo'])
            p.save()

def init_game(sender, **kwargs):
    games = (u'英雄联盟', u'格斗游戏', u'DOTA', u'炉石传说')
    for item in games:
        my_module = sender.get_model('Game')
        try:
            game = get_object_or_404(my_module, name=item)
        except Http404:
            game = my_module(name=item)
            game.save()

def init_db(sender, **kwargs):
    init_platform(sender, **kwargs)
    init_game(sender, **kwargs)


class PresentersConfig(AppConfig):
    name = 'presenters'

    def ready(self):
        post_migrate.connect(init_db, sender=self)