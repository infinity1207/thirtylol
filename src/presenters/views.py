# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from .models import Platform, Presenter, Game
import urllib, urllib2, cookielib, json
import time
import logging
from haystack.query import SearchQuerySet

logger = logging.getLogger(__name__)

def index(request):
    presenter_list = Presenter.objects.order_by('-presenterdetail__showing', '-presenterdetail__audience_count')

    # 根据平台过滤
    platform_name = request.GET.get('platform')
    if platform_name:
        presenter_list = presenter_list.filter(platform__name=platform_name)

    game_name = request.GET.get('game')
    if game_name:
        presenter_list = presenter_list.filter(game__name=game_name)

    # 根据用户输入的查询条件过滤
    q = request.GET.get('q')
    if q:
        sqs = SearchQuerySet().auto_query(q)
        q_result = []
        for item in sqs:
            if item.model_name == 'presenter':
                q_result.append(item.pk)
        presenter_list = presenter_list.filter(pk__in=q_result)

    # 分页
    per_page = 10;
    paginator = Paginator(presenter_list, per_page)
    page_number = request.GET.get('page')   # start from 1
    if not page_number:
        page_number = 1

    try:
        presenter_list = paginator.page(page_number)
    except PageNotAnInteger:
        page_number = 1
        presenter_list = paginator.page(1)
    except EmptyPage:
        page_number = paginator.num_pages
        presenter_list = paginator.page(paginator.num_pages)

    # 直播平台的分组信息
    platform_list = Platform.objects.annotate(num_presenters=Count('presenter')).order_by('-num_presenters')
    game_list = Game.objects.annotate(num_presenters=Count('presenter'))

    # 不包含页码的GET字符串
    get_list = []
    without_page_number_GET = ''
    for (k,v) in request.GET.iteritems():
        if k != 'page':
            get_list.append("%s=%s" % (k,v))
    if len(get_list) > 0:
        without_page_number_GET = "?" + "&".join(get_list)

    context = {
        'presenter_list': presenter_list,
        'page_number': int(page_number),
        'num_pages': paginator.num_pages,
        'platform_list': platform_list,
        'num_all_presenters': Presenter.objects.count(),
        'without_page_number_GET': without_page_number_GET,
        'game_list': game_list,
    }

    return render(request, 'presenters/index.html', context)

def detail(request, presenter_id):
    p = get_object_or_404(Presenter, id=presenter_id)
    context = {
        'presenter': p,
    }
    return render(request, 'presenters/detail.html', context)

def about(request):
    # print dir(request)
    return render(request, 'presenters/about.html')

def feedback(request):
    return render(request, 'presenters/feedback.html')

def fetch_huya(requst):
    # 虎牙直播
    # 貌似没有加密措施，登录后会得到一个uid
    result = []
    platform = Platform.objects.get(name=u'虎牙')
    try:
        params = json.loads(platform.login_param)
    except:
        logger.error("\tfetch presenter data from huya failed, error message: {%s}", '无效的fetch参数')
        return result

    huya_url = 'http://phone.huya.com/api/acts/reserved?uid=%s' % params['uid']
    response = urllib2.urlopen(huya_url)
    json_data = json.loads(response.read())
    if json_data['code'] != 0:
        logger.error("\tfetch presenter data from huya failed, error message: {%s}", json_data['message'])
        return result

    for data in json_data['data']:
        item = {}
        item['platform'] = u'虎牙'
        item['id_in_platform'] = data['aid']
        item['nickname'] = data['name']
        item['avatar_url'] = data['thumb']
        item['showing'] = data['isLiving']
        item['audience_count'] = data['users']
        item['room_title'] = data['contentIntro']
        result.append(item)

    logger.info("\tfetch presenter data from huya successful")
    return result

def fetch_zhanqi(request):
    # 战旗直播
    # Cookie有效期为1个月，ipad客户端退出后需要重新登录并抓取
    # 需要使用POST请求
    result = []
    platform = Platform.objects.get(name=u'战旗')
    try:
        params = json.loads(platform.login_param)
    except:
        logger.error("\tfetch presenter data from zhanqi failed, error message: {%s}", '无效的fetch参数')
        return result
    _headers = {
        "Cookie": "PHPSESSID=%s; tj_uid=%s; ZQ_GUID=%s; ZQ_GUID_C=%s" % (params['PHPSESSID'], params['tj_uid'], params['ZQ_GUID'], params['ZQ_GUID_C']),
        "User-Agent": "Zhanqi.tv Api Client",
    }

    # 传入一个空的data，urllib2函数识别到data参数则会使用POST请求
    _data = {
    }
    _rand = int(time.time())
    zhanqi_url = 'http://www.zhanqi.tv/api/user/follow.listall?_rand=%s' % (_rand)
    req = urllib2.Request(zhanqi_url, headers=_headers, data=urllib.urlencode(_data))
    response = urllib2.urlopen(req)
    json_data = json.loads(response.read())

    if json_data['code'] != 0:
        logger.error("\tfetch presenter data from zhanqi failed, error message: {%s}", json_data['message'])
        return result

    for data in json_data['data']: 
        item = {}
        item['platform'] = u'战旗'
        item['id_in_platform'] = data['uid']
        item['nickname'] = data['nickname']
        item['avatar_url'] = data['avatar'] + '-medium'
        item['gender'] = 'M' if data['gender'] == 2 else 'F'
        item['room_url'] = 'http://www.zhanqi.tv' + data['roomUrl']
        item['showing'] = True if data['status'] == "4" else False
        item['audience_count'] = int(data['online'])
        item['room_title'] = data['title']

        result.append(item)

    logger.info("\tfetch presenter data from zhanqi successful")
    return result

def fetch_panda(request, status=2):
    result = []

    panda_url = 'http://api.m.panda.tv/ajax_get_follow_rooms'
    platform = Platform.objects.get(name=u'熊猫')
    try:
        params = json.loads(platform.login_param)
    except:
        logger.error("\tfetch presenter data from panda failed, error message: {%s}", '无效的fetch参数')
        return result

    _data = {
        '__plat': 'iOS',
        '__version': '1.0.0.1048',
        'pageno': 1,
        'pagenum': 10,
        'pt_sign': params['pt_sign'],
        'pt_time': int(time.time()),
        'status': status,
    }

    M = params['M']
    R = params['R']
    # SESSCYPHP = '36d5c36ffb93c9121cc9a4ee4d959e05'
    _headers = {
        # 'Cookie': 'M=%s; R=%s; SESSCYPHP=%s' % (M, R, SESSCYPHP),
        'Cookie': 'M=%s; R=%s;' % (M, R),
        'User-Agent': 'PandaTV-ios/1.0.0 (iPhone; iOS 9.1; Scale/3.00)',
        'Xiaozhangdepandatv': 1,
        'Connection': 'keep-alive',
    }

    req = urllib2.Request(panda_url, headers=_headers, data=urllib.urlencode(_data))
    response = urllib2.urlopen(req)
    json_data = json.loads(response.read())

    for data in json_data['data']['items']:
        item = {}
        item['platform'] = u'熊猫'
        item['id_in_platform'] = data['userinfo']['rid']
        item['nickname'] = data['userinfo']['nickName']
        item['avatar_url'] = data['userinfo']['avatar']
        item['room_url'] = "http://www.panda.tv/%s" % data['id']
        item['showing'] = True if status == 2 else False
        item['audience_count'] = data['person_num']
        item['room_title'] = data['name']
        result.append(item)

    logger.info("\tfetch presenter data from panda successful")
    return result


def fetch_douyu(request):
    result = []

    platform = Platform.objects.get(name=u'斗鱼')
    try:
        params = json.loads(platform.login_param)
    except:
        logger.error("\tfetch presenter data from douyu failed, error message: {%s}", '无效的fetch参数')
        return result

    _time = int(time.time())
    douyu_url = 'http://www.douyutv.com/api/v1/follow?aid=ios&limit=100&time=%s&client_sys=ios&offset=0&count=28&token=%s&auth=%s' % (_time, params['token'], params['auth'])
    req = urllib2.Request(douyu_url)
    response = urllib2.urlopen(req)
    json_data = json.loads(response.read())
    if 'error' in json_data and json_data['error'] > 0:
        logger.error("\tfetch presenter data from douyu failed, error message: {%s}", json_data['data'])
        return result

    for data in json_data['data']: 
        item = {}
        item['platform'] = u'斗鱼'
        item['id_in_platform'] = data['owner_uid']
        item['nickname'] = data['nickname']
        item['avatar_url'] = "http://uc.douyutv.com/avatar.php?uid=%s&size=middle" % data['owner_uid']
        item['room_url'] = 'http://www.douyutv.com' + data['url']
        item['showing'] = True if data['show_status'] == '1' else False
        item['audience_count'] = data['online']
        item['room_title'] = data['room_name']
        result.append(item)

    logger.info("\tfetch presenter data from douyu successful")
    return result

def fetch_longzhu(request):
    # 龙珠直播
    # 发送json请求时会在Cookie里放入plu_id
    # plu_id采取登录后从Charles中抓取
    result = []
    platform = Platform.objects.get(name=u'龙珠')
    try:
        params = json.loads(platform.login_param)
    except:
        logger.error("\tfetch presenter data from longzhu failed, error message: {%s}", '无效的fetch参数')
        return result

    plu_id = params['plu_id']
    longzhu_url = 'http://star.api.plu.cn/RoomSubscription/UserSubsciptionListForAll?isLive=0&liveSource=0&pageIndex=1&pageSize=10'
    _headers = {
        "Cookie": 'p1u_id=%s' % (plu_id)
    }
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    req = urllib2.Request(longzhu_url, headers=_headers)
    response = opener.open(req)
    json_data = json.loads(response.read())

    for data in json_data['Data']:
        item = {}
        item['platform'] = Platform.objects.get(name=u'龙珠')
        item['id_in_platform'] = data['RoomId']
        item['nickname'] = data['RoomName']
        item['avatar_url'] = data['Avatar']
        item['room_url'] = 'http://star.longzhu.com/%s'% data['Domain']
        item['showing'] = data['IsLive']

        if item['showing']:
            # 获取房间信息(观众人数)
            PLULOGINSESSID = params['PLULOGINSESSID']
            room_detail = _fetch_longzhu_room_detail(plu_id, PLULOGINSESSID, data['Domain'])
            item['audience_count'] = room_detail['OnlineCount']
            item['room_title'] = room_detail['BaseRoomInfo']['BoardCastTitle']
        else:
            item['audience_count'] = 0

        result.append(item)

    logger.info("\tfetch presenter data from longzhu successful")
    return result

def _fetch_longzhu_room_detail(plu_id, plu_login_sessid, domain):
    # 获得房间详细信息(观众人数……)
    room_info_url = 'http://star.apicdn.plu.cn/room/GetInfoJsonp?domain=%s' % domain
    _headers = {
        "Cookie": 'p1u_id=%s; PLULOGINSESSID=%s' % (plu_id, plu_login_sessid)
    }
    req = urllib2.Request(room_info_url, headers=_headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def fetch(request):
    logger.info('fetch presenter data start')

    result = []
    result.extend(fetch_douyu(request))
    result.extend(fetch_huya(request))
    result.extend(fetch_zhanqi(request))
    result.extend(fetch_longzhu(request))
    result.extend(fetch_panda(request,status=2))
    result.extend(fetch_panda(request,status=3))

    for item in result:
        try:
            p = get_object_or_404(
                Presenter, 
                platform__name=item['platform'], 
                id_in_platform=item['id_in_platform'])
        except Http404:
            p = Presenter()
            p.platform = Platform.objects.get(name=item['platform'])
            p.id_in_platform = item['id_in_platform']
            p.nickname = item['nickname']
            p.avatar_url = item.get('avatar_url')
            p.gender = item.get('gender', 'M')
            p.room_url = item.get('room_url', 'http://www.30lol.com')
            p.save()

        p.presenterdetail.showing = item['showing']
        p.presenterdetail.room_title = item.get('room_title', '')
        p.presenterdetail.audience_count = item['audience_count']
        p.presenterdetail.save()

    logger.info('fetch presenter data done')

    return HttpResponse('fetch complete...')
