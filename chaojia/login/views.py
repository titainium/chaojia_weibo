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
from weibo import APIClient
import time
import redis

APP_KEY = settings.APP_KEY
APP_SECRET = settings.APP_SECRET
CALLBACK_URL = settings.CALLBACK_URL
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
myredis = redis.StrictRedis(host='localhost', port=6379, db=0)

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
    myredis.set("user_"+uid,userProfile)
    request.session['uid'] = uid
    request.session['screen_name'] = userProfile['screen_name']
    myredis.ltrim('token_'+uid,start=1,end=0)
    myredis.lpush('token_'+uid,expires_in,access_token)
    
    return HttpResponseRedirect("/oauth/start")

def loginout(request):
    
    try:
        del request.session['uid']
    except:
        pass
    
    return HttpResponseRedirect("/oauth/start")


def home(request):
    
   
    c = RequestContext(request,{

    })  
    
    return render_to_response('base.html',c) 
