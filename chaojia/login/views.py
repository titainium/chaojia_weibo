#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
created by Mingyou(378868467@qq.com) on 2012-06-17
www.chaojia.me All rights reserved
'''
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from chaojia.weibo import APIClient
import time
import redis

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

def use_sina_login(request):
    
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    
    return HttpResponseRedirect(client.get_authorize_url())
   

def sina_login_suc(request):
    
    code = request.GET['code']
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    r = client.request_access_token(code)
    access_token = r.access_token
    expires_in = r.expires_in
    client.set_access_token(access_token, expires_in)
    uid = str(client.get.account__get_uid()["uid"])
    userProfile = client.users__show(uid=uid)
    loginRedis.set("user_"+uid,userProfile)
    request.session['uid'] = uid
    request.session['screen_name'] = userProfile['screen_name']
    loginRedis.ltrim('token_'+uid,start=1,end=0)
    loginRedis.lpush('token_'+uid,expires_in,access_token)
    if 'ponit_'+uid not in PRedis.keys():
        PRedis.hset('ponit_'+uid,'current_point',10)
        PRedis.hset('ponit_'+uid,'time',1)
    if 'ph_'+uid not in PHRedis.keys():
       dt = {"current_point":10,
            "previous_point":0,
            "change_point":"+10",
            "change_time":time.strftime("%Y-%m-%d %H:%M:%S"),
            "change_reason":"用户新注册", }
       PHRedis.lpush('ph_'+uid,dt)
    
    return HttpResponseRedirect("/oauth/start")

def loginout(request):
    
    try:
        del request.session['uid']
    except:
        pass
    
    return HttpResponseRedirect("/oauth/start")


def home(request):
    try:
        uid = str(request.session["uid"])
        if int(time.time()) > int(loginRedis.lindex("token_"+uid,1)):
            del request.session['uid']
    except:
        pass
    
    c = RequestContext(request,{

    })  
    
    return render_to_response('base.html',c) 
