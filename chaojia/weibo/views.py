#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse
from provider import provider 
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from chaojia.weibo import APIClient
import redis
import time

APP_KEY = settings.APP_KEY
APP_SECRET = settings.APP_SECRET
CALLBACK_URL = settings.CALLBACK_URL
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)

login_redis_host = settings.LOGIN_REDIS_HOST
login_redis_port = int(settings.LOGIN_REDIS_PORT)
login_redis_db = int(settings.LOGIN_REDIS_DB)
loginRedis = redis.StrictRedis(host=login_redis_host, port=login_redis_port, db=login_redis_db)

ponit_redis_host = settings.PONIT_REDIS_HOST
ponit_redis_port = int(settings.PONIT_REDIS_PORT)
ponit_redis_db = int(settings.PONIT_REDIS_DB)
PRedis = redis.StrictRedis(host=ponit_redis_host, port=ponit_redis_port, db=ponit_redis_db)

ponit_history_redis_host = settings.PONIT_HISTORY_REDIS_HOST
ponit_history_redis_port = int(settings.PONIT_HISTORY_REDIS_PORT)
ponit_history_redis_db = int(settings.PONIT_HISTORY_REDIS_DB)
PHRedis = redis.StrictRedis(host=ponit_history_redis_host, port=ponit_history_redis_port, db=ponit_history_redis_db)

weibo_redis_host = settings.WEIBO_REDIS_HOST
weibo_redis_port = int(settings.WEIBO_REDIS_PORT)
weibo_redis_db = int(settings.WEIBO_REDIS_DB)
weiboRedis = redis.StrictRedis(host=weibo_redis_host, port=weibo_redis_port, db=weibo_redis_db)

admin_redis_host = settings.ADMIN_REDIS_HOST
admin_redis_port = int(settings.ADMIN_REDIS_PORT)
admin_redis_db = int(settings.ADMIN_REDIS_DB)
adminRedis = redis.StrictRedis(host=admin_redis_host,port=admin_redis_port, db=admin_redis_db)

def weibo_home(request):
    try:        
        uid = str(request.session["uid"])
        if int(time.time()) > int(loginRedis.lindex("token_"+uid,1)):
            raise
        access_token = loginRedis.lindex("token_"+uid,0)
        expires_in = loginRedis.lindex("token_"+uid,1)
        client.set_access_token(access_token, expires_in)
    except:
        
        return HttpResponseRedirect("/oauth/start")    
    tags = []
    for i in client.tags(uid=uid):
        for l in i.keys():
            if l != "weight":
                tags.append(i[l])
    
    wids = set()
    for tag in tags:
        result = provider.getWeiboIdByTag(tag)
        if result == None:
            continue
        wids = wids | result
    
    wids = provider.filterZF(uid, wids)#过滤3小时内转发过的微博id
    zhiding_wids = provider.getZhiDingWid(uid)#用户获取置顶的微博id
    
    #获取3小时内没有转发过的微博信息
    weibos = []
    for wid in wids:
        weibo = provider.getWeiboById(wid)
        if weibo == None:
            continue
        weibo = eval(weibo)
        weibos.append(weibo)
    
    #获取置顶的微博信息
    zhiding_weibos = []
    for wid in zhiding_wids:
        weibo = provider.getWeiboById(wid)
        if weibo == None:
            continue
        weibo = eval(weibo)
        zhiding_weibos.append(weibo)
    
    c = RequestContext(request,{
        "zhiding_weibos":zhiding_weibos,
        "weibos": weibos,
    })
    return render_to_response('weibo_home.html',c)  


def zf_choose(request):
    '''author: Mingyou(378868467@qq.com) 2012-06-26'''
    
    def getPoint(key):
        import random
        result = adminRedis.lrange(key,0,-1)
        if result == []:
            x = ""
        else:
            x = random.choice(result)
        return x
    dt = {"y":"ponit_assent","n":"ponit_refusal","m":"ponit_neutral"}
    point = request.GET['point']
    wid = str(request.GET['id'])
    result = '''
    <form action="/weibo/zf/weibo/">
    请输入140字以内的评论:<br>
    <textarea name="t">%s</textarea><br>
    <input type="hidden" name="id" value="%s"><br>
    是否评论原微博: <input type="checkbox" name="is_comment" value="2">
    <input type="submit" value="确定转发">

   ''' % (getPoint(dt[point]), wid)
    
    return HttpResponse(result)

def zf_weibo(request):
    '''author: Mingyou(378868467@qq.com) 2012-06-25'''
    
    try:        
        wid = str(request.GET['id'])
        uid = str(request.session["uid"])
        status = request.GET['t']
        if int(time.time()) > int(loginRedis.lindex("token_"+uid,1)):
            raise
        access_token = loginRedis.lindex("token_"+uid,0)
        expires_in = loginRedis.lindex("token_"+uid,1)
        client.set_access_token(access_token, expires_in)
    except:
        return HttpResponseRedirect("/oauth/start")    
    
    if weiboRedis.get('overdue_'+uid+'_'+wid) != None:
        return HttpResponse('3小时内不能转发同一条微博 !')
    is_comment = 0
    if request.GET.has_key('is_comment'):
        is_comment = request.GET['is_comment']
    try:
        client.post.statuses__repost(id = wid, status = status,is_comment=is_comment)
    except:
        return HttpResponse("network error. pls try again...")
    userCurPonit = int(PRedis.hget('ponit_'+uid,'current_point'))
    userTimePonit = int(PRedis.hget('ponit_'+uid,'time'))
    PRedis.hset('ponit_'+uid,'current_point',userCurPonit + 1*userTimePonit)
    dt = eval(PHRedis.lindex('ph_'+uid,0))
    dt['change_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    dt['current_point'] = userCurPonit + 1*userTimePonit
    dt['previous_point'] = userCurPonit
    dt['change_point'] = '+'+str(1*userTimePonit)
    dt['change_reason'] = '用户转发微博,倍率: '+ str(userTimePonit)
    PHRedis.lpush('ph_'+uid,dt)
    keyTime = time.strftime("%Y%m%d%H")
    if PHRedis.hget("phh_"+uid,keyTime) == None:
        PHRedis.hset("phh_"+uid,keyTime,1)
    else:
        phhPonit = 1 + int(PHRedis.hget("phh_"+uid,keyTime))
        PHRedis.hset("phh_"+uid,keyTime,phhPonit)
    weiboRedis.setex('overdue_'+uid+'_'+wid,10800,time.strftime("%Y-%m-%d %H:%M:%S"))
    
    return HttpResponse("转发成功,积分 +"+str(1*userTimePonit))


def qzf(request):
    '''author: Mingyou(378868467@qq.com) 2012-06-21'''
    
    wbls = []
    class checkwb(object):
        def __init__(self,value,uid):
            self.uid = uid
            self.id = value['id']
            self.text = value['text']
            self.created_at = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime(value['created_at'],"%a %b %d %H:%M:%S +0800 %Y"))
            self.reposts_count = value['reposts_count']
            self.comments_count = value['comments_count']
        def check_zf(self,tags):
            for t in tags:
                if weiboRedis.sismember(str(t.encode("utf-8"))+"_weiboids",self.id):
                    self.zf = True
                    break
                else:
                    self.zf = False
            return self
    
    try:
        uid = str(request.session["uid"])
        if int(time.time()) > int(loginRedis.lindex("token_"+uid,1)):
            raise
        access_token = loginRedis.lindex("token_"+uid,0)
        expires_in = loginRedis.lindex("token_"+uid,1)
        client.set_access_token(access_token, expires_in) 
    except:
        
        return HttpResponseRedirect("/oauth/start")   #user no login, redirect to login page
    
    tags = []
    for i in client.tags(uid=uid):
        for l in i.keys():
            if l != "weight":
                tags.append(i[l])
    
    for w in client.get.statuses__user_timeline().statuses:
        wbls.append(checkwb(w,uid).check_zf(tags))
    
    c = RequestContext(request,{
        "weibos":wbls,

    })
    
    return render_to_response('qzf.html',c)


def choose_weibo_qzf(request):
    '''author: Mingyou(378868467@qq.com) 2012-06-21'''
    
    wid = str(request.GET['id'])
    try:
        uid = str(request.session["uid"])
        if int(time.time()) > int(loginRedis.lindex("token_"+uid,1)):
            raise
        access_token = loginRedis.lindex("token_"+uid,0)
        expires_in = loginRedis.lindex("token_"+uid,1)
        client.set_access_token(access_token, expires_in) 
    except:
        
        return HttpResponseRedirect("/oauth/start")   #user no login, redirect to login page
    
    weibo = client.statuses__show(id=wid)
    weibo['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime(weibo['created_at'],"%a %b %d %H:%M:%S +0800 %Y"))
    
    if request.GET.has_key('zfsh'):
        if wid in adminRedis.hkeys("shenheweiboguanggao"):
            result = "您已提交过此审核,请耐心等待工作人员处理,谢谢."
        else:
            adminRedis.hset("shenheweiboguanggao",wid,time.strftime("%Y-%m-%d %H:%M:%S"))
            result = "已成功提交审核,我们会尽快除理,谢谢."
        return HttpResponse(result)
    
    if request.GET.has_key('zf'):
        weiboRedis.set("weiboid_"+str(weibo['id']),weibo)
        
        for i in request.GET.getlist("tags"):
            weiboRedis.sadd(str(i.encode('utf-8'))+"_weiboids",weibo['id'])
        
        return HttpResponseRedirect("../../qzf/")
    text = weibo['text']
    reposts_count = weibo['reposts_count']
    comments_count = weibo['comments_count']
    created_at = weibo['created_at']
    tags = [];gg = False
    if int(PRedis.hget('ponit_'+uid,'current_point')) >= 20 and "http:" in text:
        gg = True
    for i in client.tags(uid=uid):
        for l in i.keys():
            if l != "weight":
                tags.append(i[l])
    
    c = RequestContext(request,{
        "id":wid,
        "text":text,
        "reposts_count":reposts_count,
        "comments_count":comments_count,
        "created_at":created_at,
        "tags":tags,
        "gg":gg,

    })
    
    return render_to_response('qzf_choose.html',c)



