#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
created by Mingyou on 2012-06-17
www.chaojia.me All rights reserved
'''
from django.template import Context
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseRedirect
from weibo import APIClient
import time
import redis

APP_KEY = '' # app key
APP_SECRET = '' # app secret
CALLBACK_URL = '' # callback url

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
    uid = client.get.account__get_uid()["uid"]
    request.session['uid'] = uid
    myredis.ltrim('token_'+str(uid),start=1,end=0)
    myredis.lpush('token_'+str(uid),expires_in,access_token)
    
    return HttpResponse("your uid: "+str(client.get.account__get_uid())+"<br />your weibo: "+client.get.statuses__user_timeline()["statuses"][0]["text"].encode("utf-8"))

def fortest(request):
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    access_token = myredis.lindex("token_"+str(request.session['uid']),0)
    expires_in = myredis.lindex("token_"+str(request.session['uid']),1)
    client.set_access_token(access_token, expires_in)
    uid = request.session['uid']
    return HttpResponse("your uid: "+str(uid)+"<br />your weibo: "+client.get.statuses__user_timeline()["statuses"][0]["text"].encode("utf-8"))

def home(request):
    c = '''
    <body>
    <a href="/oauth/login"><img src="http://www.sinaimg.cn/blog/developer/wiki/32.png"/></a>
    </body>
    '''
    try:
        uid = request.session['uid']
        if int(time.time()) < int(myredis.lindex("token_"+str(uid),1)):
            c = "welcome, %d" % uid
    except:
        pass
    return HttpResponse(c)
