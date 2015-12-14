# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
# from django.utils.crypto import salted_hmac
from django.contrib.auth.models import User
from django.dispatch import receiver
from userena.models import UserenaBaseProfile
# from userena.models import UserenaSignup
from userena.signals import signup_complete
from userena.utils import get_user_profile

class OAuth(models.Model):
    user = models.OneToOneField(User)   

    # account = models.CharField(max_length=50)
    token = models.CharField(max_length=128)
    uid = models.CharField(max_length=128)
    expired = models.DateTimeField()


class UserSource(models.Model):
    flag = models.IntegerField()    # 0: 管理员添加, 10: 网站注册，大于等于100: OAuth
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class UserProfile(UserenaBaseProfile):
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='my_profile')

    source = models.ForeignKey('UserSource', null=True)

    favourite_snack = models.CharField(_('favourite snack'),
                                       max_length=5)

    follows = models.ManyToManyField('presenters.Presenter')
    
    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        if self.pk is None:
            self.source = UserSource.objects.get(flag=0)


@receiver(signup_complete, sender=None)
def update_user_source(sender, user, *args, **kwargs):
    profile = get_user_profile(user)
    profile.source = UserSource.objects.get(flag=10)
    profile.save()

