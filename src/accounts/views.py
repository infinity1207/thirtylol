# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
# from django.core.urlresolvers import reverse
# from django.http import Http404
from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from userena.utils import signin_redirect, get_user_profile
from userena import views as userena_views
import json
from .models import UserSource
from .forms import EditProfileForm
from presenters.models import Presenter
from thirtylol import settings
import urllib, urllib2

def oauth(request):
    try:
        code = request.GET.get('code', '')
        token_str = _access_token(request, code)
        token_json = json.loads(token_str)
        user = authenticate(token=token_json['access_token'], uid=token_json['uid'], expire_in=(60 * 60 * 24))
        if user:
            try:
                user_str = _show_user(token_json['access_token'], token_json['uid'])
                user_json = json.loads(user_str)
                user.username = user_json['screen_name']
                user.save()
            except:
                pass
            
            auth_login(request, user)
            profile = get_user_profile(user)
            profile.source = UserSource.objects.get(flag=100)
            profile.save()
            return HttpResponseRedirect(signin_redirect(user=user))
    except:
        return HttpResponse("很抱歉，使用新浪微博认证登录失败，请尝试从网站注册！")

def request(url, method='GET', headers={}, params=None):
    data = None
    if params:
         data = urllib.urlencode(params)

    if method.upper() == 'GET':
        url = url + '?' + data
        data = None

    req = urllib2.Request(url, data=data, headers=headers)
    resp = urllib2.urlopen(req)
    return resp.info(), resp.read()

def _show_user(access_token, uid):
    show_user_url = 'https://api.weibo.com/2/users/show.json'
    params = {
        'access_token': access_token,
        'uid': uid,
    }
    return request(show_user_url, params=params)[1]


def _access_token(request, code):
    access_token_url = 'https://api.weibo.com/oauth2/access_token'
    params = {
        'client_id': settings.WEIBO_OAUTH_APP_KEY,
        'client_secret': settings.WEIBO_OAUTH_APP_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': "http://%s/oauth/" % (request.get_host()),
    }
    req = urllib2.Request(access_token_url, data=urllib.urlencode(params))
    return urllib2.urlopen(req).read()

def signin(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('userena_profile_detail', kwargs={'username':request.user.username}))
    return userena_views.signin(request, template_name='accounts/signin.html') 

def profile_edit(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_user_profile(user)

    if request.method == 'POST':
        print request.POST
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            mugshot = form.cleaned_data['mugshot']
            if mugshot:
                profile.mugshot = form.cleaned_data['mugshot']
                profile.save()
    else:
        form = EditProfileForm()

    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'accounts/edit.html', context)

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_user_profile(user)
    context = {
        'profile': profile,
    }
    return render(request, 'accounts/detail.html', context)

def favourite(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_user_profile(user)

    presenter_list = user.my_profile.follows.order_by('-presenterdetail__showing', '-presenterdetail__audience_count');
    context = {
        'profile': profile,
        'presenter_list': presenter_list,
    }
    return render(request, 'accounts/favourite.html', context)

def follow(request):
    if not request.is_ajax():
        raise Http404()

    user_id = request.POST.get('user_id', None)
    presenter_id = request.POST.get('presenter_id', None)

    user = User.objects.get(id=user_id)
    presenter = Presenter.objects.get(id=presenter_id)

    if presenter not in user.my_profile.follows.all():
        user.my_profile.follows.add(presenter)
        user.my_profile.save()

    return HttpResponse(json.dumps({'num_follows':presenter.userprofile_set.count()}), content_type='application/json')

def unfollow(request):
    if not request.is_ajax():
        raise Http404()

    user_id = request.POST.get('user_id', None)
    presenter_id = request.POST.get('presenter_id', None)

    user = User.objects.get(id=user_id)
    presenter = Presenter.objects.get(id=presenter_id)

    if presenter in user.my_profile.follows.all():
        user.my_profile.follows.remove(presenter)
        user.my_profile.save()

    return HttpResponse(json.dumps({'num_follows':presenter.userprofile_set.count()}), content_type='application/json')