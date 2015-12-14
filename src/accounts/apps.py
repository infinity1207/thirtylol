# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.db.models.signals import post_migrate

def init_db(sender, **kwargs):
    _datas = [
        (0, u'管理员添加'),
        (10, u'网站注册'),
        (100, u'微博登录'),
    ]
    for data in _datas:
        my_module = sender.get_model('UserSource')
        try:
            us = my_module.objects.get(flag=data[0])
        except my_module.DoesNotExist:
            us = my_module(flag=data[0], name=data[1])
            us.save()

class AccountsConfig(AppConfig):
    name = 'accounts'
    
    def ready(self):
        post_migrate.connect(init_db, sender=self)
