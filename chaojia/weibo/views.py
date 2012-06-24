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
myredis = redis.StrictRedis(host='localhost', port=6379, db=0)

def weibo_home(request):
    try:        
        uid = str(request.session["uid"])
        if int(time.time()) > int(myredis.lindex("token_"+uid,1)):
            raise
        access_token = myredis.lindex("token_"+uid,0)
        expires_in = myredis.lindex("token_"+uid,1)
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
        wids = wids | result
    
    wids = provider.filterZF(uid, wids)#过滤3小时内转发过的微博id
    zhiding_wids = provider.getZhiDingWid(uid)#用户获取置顶的微博id
    
    #获取3小时内没有转发过的微博信息
    weibos = []
    for wid in wids:
        weibo = provider.getWeiboById(wid)
        weibo = eval(weibo)
        weibos.append(weibo)
    
    #获取置顶的微博信息
    zhiding_weibos = []
    for wid in zhiding_wids:
        weibo = provider.getWeiboById(wid)
        weibo = eval(weibo)
        zhiding_weibos.append(weibo)
    
    c = RequestContext(request,{
        "zhiding_weibos":zhiding_weibos,
        "weibos": weibos,
    })
    return render_to_response('weibo_home.html',c)    

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
                if myredis.sismember(str(t.encode("utf-8"))+"_weiboids",self.id):
                    self.zf = True
                    break
                else:
                    self.zf = False
            return self
    
    try:
        uid = str(request.session["uid"])
        if int(time.time()) > int(myredis.lindex("token_"+uid,1)):
            raise
        access_token = myredis.lindex("token_"+uid,0)
        expires_in = myredis.lindex("token_"+uid,1)
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


def choose_weibo_zf(request):
    '''author: Mingyou(378868467@qq.com) 2012-06-21'''
    
    id = str(request.GET['id'])
    try:
        uid = str(request.session["uid"])
        if int(time.time()) > int(myredis.lindex("token_"+uid,1)):
            raise
        access_token = myredis.lindex("token_"+uid,0)
        expires_in = myredis.lindex("token_"+uid,1)
        client.set_access_token(access_token, expires_in) 
    except:
        
        return HttpResponseRedirect("/oauth/start")   #user no login, redirect to login page
    
    weibo = client.statuses__show(id=id)
    weibo['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime(weibo['created_at'],"%a %b %d %H:%M:%S +0800 %Y"))
    if request.GET.has_key('zf'):
        myredis.set("weiboid_"+str(weibo['id']),weibo)
        
        for i in request.GET.getlist("tags"):
            myredis.sadd(str(i.encode('utf-8'))+"_weiboids",weibo['id'])
        
        return HttpResponseRedirect("/weibo/qzf/")
    text = weibo['text']
    reposts_count = weibo['reposts_count']
    comments_count = weibo['comments_count']
    created_at = weibo['created_at']
    tags = []
    for i in client.tags(uid=uid):
        for l in i.keys():
            if l != "weight":
                tags.append(i[l])
    
    c = RequestContext(request,{
        "id":id,
        "text":text,
        "reposts_count":reposts_count,
        "comments_count":comments_count,
        "created_at":created_at,
        "tags":tags,

    })
    
    return render_to_response('qzf_choose.html',c)



