#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse
from provider import provider 
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from chaojia.weiboapi import APIClient
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
        if int(time.time()) > int(loginRedis.hget("token_"+uid,"expires_in")):
            raise
        access_token = loginRedis.hget("token_"+uid,"access_token")
        expires_in = loginRedis.hget("token_"+uid,"expires_in")
        client.set_access_token(access_token, expires_in)
    except:
        
        return HttpResponseRedirect("/oauth/start")    
    tags = []
    for i in client.tags(uid=uid):
        for l in i.keys():
            if l != "weight":
                tags.append(i[l])
    
    tag_wids = []
    for tag in tags:
        result = provider.getWeiboIdByTag(tag)
        if result == None:
            continue
        tw = {tag:result}
        tag_wids.append(tw)
    
    data = {}
    for tw in tag_wids:
        wids = provider.filterZF(uid, tw.values()[0])#过滤3小时内转发过的微博id
        data[tw.keys()[0]] = wids
        
    zhiding_wids = provider.getZhiDingWid(uid)#用户获取置顶的微博id
    
    #获取3小时内没有转发过的微博信息
    weibos = []
    for d in data.keys():
        for wid in data[d]:
            weibo = provider.getWeiboById(wid)
            if weibo == None:
                continue
            weibo = eval(weibo)
            weibo['tag'] = d
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
        "tags":tags
    })
    return render_to_response('weibo_home.html',c)  

def weibo_tags(request):
    try:        
        uid = str(request.session["uid"])
        if int(time.time()) > int(loginRedis.hget("token_"+uid,"expires_in")):
            raise
        access_token = loginRedis.hget("token_"+uid,"access_token")
        expires_in = loginRedis.hget("token_"+uid,"expires_in")
        client.set_access_token(access_token, expires_in)
    except:
        
        return HttpResponseRedirect("/oauth/start")
    tags = []
    for i in client.tags(uid=uid):
        for l in i.keys():
            if l != "weight":
                tags.append(i[l])
    
    tag = request.GET['tags']
    
    tag_wids = []
    result = provider.getWeiboIdByTag(tag)
    if result == None:
        result = []
    tw = {tag:result}
    tag_wids.append(tw)
    
    data = {}
    for tw in tag_wids:
        wids = provider.filterZF(uid, tw.values()[0])#过滤3小时内转发过的微博id
        data[tw.keys()[0]] = wids
    
    #获取3小时内没有转发过的微博信息
    weibos = []
    for d in data.keys():
        for wid in data[d]:
            weibo = provider.getWeiboById(wid)
            if weibo == None:
                continue
            weibo = eval(weibo)
            weibo['tag'] = d
            weibos.append(weibo)
    
    c = RequestContext(request,{
        "weibos": weibos,
        "tags":tags,
        "select_tag":tag
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
    def ponitOpe(uid,point,reason):
        userCurPonit = int(PRedis.hget('ponit_'+uid,'current_point'))
        userTimePonit = int(PRedis.hget('ponit_'+uid,'time'))
        PRedis.hset('ponit_'+uid,'current_point',userCurPonit + point*userTimePonit)
        dt = eval(PHRedis.lindex('ph_'+uid,0))
        dt['change_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
        dt['current_point'] = userCurPonit + point*userTimePonit
        dt['previous_point'] = userCurPonit
        dt['change_point'] = '+'+str(point*userTimePonit)
        dt['change_reason'] = reason + str(userTimePonit)
        PHRedis.lpush('ph_'+uid,dt)
        keyTime = time.strftime("%Y%m%d%H")
        if PHRedis.hget("phh_"+uid,keyTime) == None:
            PHRedis.hset("phh_"+uid,keyTime,point*userTimePonit)
        else:
            phhPonit = point*userTimePonit + int(PHRedis.hget("phh_"+uid,keyTime))
            PHRedis.hset("phh_"+uid,keyTime,phhPonit)
        
        return str(point*userTimePonit) 
    try:        
        wid = str(request.GET['id'])
        uid = str(request.session["uid"])
        status = request.GET['t']
        if int(time.time()) > int(loginRedis.hget("token_"+uid,"expires_in")):
            raise
        access_token = loginRedis.hget("token_"+uid,"access_token")
        expires_in = loginRedis.hget("token_"+uid,"expires_in")
        client.set_access_token(access_token, expires_in)
    except:
        return HttpResponseRedirect("/oauth/start")    
    
    wb = eval(weiboRedis.get("weiboid_"+wid))
    wuid = str(wb['user']['id'])
    wb['reposts_count'] = 1 + int(wb['reposts_count'])
    if weiboRedis.get('overdue_'+uid+'_'+wid) != None:
        return HttpResponse('3小时内不能转发同一条微博 !')
    if wuid == uid:
        return HttpResponse('自己不能转发自己的微博 !')
    is_comment = 0
    if request.GET.has_key('is_comment'):
        is_comment = request.GET['is_comment']
        wb['comments_count'] = 1 + int(wb['comments_count'])
    wuserCurPonit = int(PRedis.hget('ponit_'+wuid,'current_point'))
    if u"广告" in wb['tags']:
        if wuserCurPonit >= 20:
            userCurPonit = int(PRedis.hget('ponit_gg_'+uid,'current_point'))
            if userCurPonit >= 1 :
                PRedis.hset('ponit_gg_'+uid,'current_point',userCurPonit - 1)
                PRedis.hset('ponit_'+wuid,'current_point',wuserCurPonit - 20)
                try:
                    client.post.statuses__repost(id = wid, status = status,is_comment=is_comment)
                    weiboRedis.zadd("weiboid_order_hot",int(wb['reposts_count'])+int(wb['comments_count']),wid)
                    weiboRedis.set("weiboid_"+wid,wb)
                    weiboRedis.setex('overdue_'+uid+'_'+wid,10800,time.strftime("%Y-%m-%d %H:%M:%S"))
                except:
                    return HttpResponse("network error. pls try again...")
                return HttpResponse("转发广告微博成功,积分 +"+ponitOpe(uid,20,"转发广告微博,倍率: "))
            else:
                return HttpResponse("您的广告积分不够,不能转发此广告微博")
        else:
            return HttpResponse("该广告微博用户积分不够,您不能转发.")
    
    else:
       if wuserCurPonit >= 1:
            PRedis.hset('ponit_'+wuid,'current_point',wuserCurPonit - 1)
            try:
                client.post.statuses__repost(id = wid, status = status,is_comment=is_comment)
                weiboRedis.zadd("weiboid_order_hot",int(wb['reposts_count'])+int(wb['comments_count']),wid)
                weiboRedis.set("weiboid_"+wid,wb)
                weiboRedis.setex('overdue_'+uid+'_'+wid,10800,time.strftime("%Y-%m-%d %H:%M:%S"))
            except:
                return HttpResponse("network error. pls try again...")
            return HttpResponse("转发成功,积分 +"+ponitOpe(uid,1,"转发微博,倍率: "))
       else:
            return HttpResponse("该微博用户积分不够,您不能转发.")

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
        def check_zf(self):
            if adminRedis.hexists("shenheweiboguanggao",self.id):
                self.zf = "sh"
            elif weiboRedis.zrevrank("weiboid_order_time",self.id) != None:
                self.zf = "zf"
            else:
                self.zf = False
            return self
    
    try:
        uid = str(request.session["uid"])
        if int(time.time()) > int(loginRedis.hget("token_"+uid,"expires_in")):
            raise
        access_token = loginRedis.hget("token_"+uid,"access_token")
        expires_in = loginRedis.hget("token_"+uid,"expires_in")
        client.set_access_token(access_token, expires_in) 
    except:
        
        return HttpResponseRedirect("/oauth/start")   #user no login, redirect to login page
    
    for w in client.get.statuses__user_timeline().statuses:
        wbls.append(checkwb(w,uid).check_zf())
    
    c = RequestContext(request,{
        "weibos":wbls,

    })
    
    return render_to_response('qzf.html',c)


def choose_weibo_qzf(request):
    '''author: Mingyou(378868467@qq.com) 2012-06-21'''
    wid = str(request.GET['id'])
    try:
        uid = str(request.session["uid"])
        if int(time.time()) > int(loginRedis.hget("token_"+uid,"expires_in")):
            raise
        access_token = loginRedis.hget("token_"+uid,"access_token")
        expires_in = loginRedis.hget("token_"+uid,"expires_in")
        client.set_access_token(access_token, expires_in) 
    except:
        
        return HttpResponseRedirect("/oauth/start")   #user no login, redirect to login page
    
    weibo = client.statuses__show(id=wid)
    weibo['created_at'] = time.strftime("%Y-%m-%d %H:%M:%S",time.strptime(weibo['created_at'],"%a %b %d %H:%M:%S +0800 %Y"))
    
    if request.GET.has_key('zfsh'):
        tags = request.GET.getlist("tags")
        if wid in adminRedis.hkeys("shenheweiboguanggao"):
            result = "您已提交过此审核,请耐心等待工作人员处理,谢谢."
        
        elif weiboRedis.zrevrank("weiboid_order_time",wid) != None:
            result = "您已经求转发过此微博."
               
        else:
            adminRedis.hset("shenheweiboguanggao",wid,time.strftime("%Y-%m-%d %H:%M:%S"))
            weibo['tags'] = tags
            weibo['reposts_count'] = 0
            weibo['comments_count'] = 0
            weiboRedis.set("weiboid_"+wid,weibo)
            result = "已成功提交审核,我们会尽快除理,谢谢."
        return HttpResponse(result)
    
    if request.GET.has_key('zf'):
        weibo['tags'] = request.GET.getlist("tags")
        weibo['reposts_count'] = 0
        weibo['comments_count'] = 0
        weiboRedis.set("weiboid_"+wid,weibo)
        weiboRedis.zadd("weiboid_order_time",time.strftime("%Y%m%d%H%M%S"),wid)
        weiboRedis.zadd("weiboid_order_hot",0,wid)
        
        for i in request.GET.getlist("tags"):
            weiboRedis.sadd(str(i.encode('utf-8'))+"_weiboids",weibo['id'])
        
        return HttpResponseRedirect("../../qzf/")
    text = weibo['text']
    reposts_count = weibo['reposts_count']
    comments_count = weibo['comments_count']
    created_at = weibo['created_at']
    tags = [];gg = False
    if int(PRedis.hget('ponit_gg_'+uid,'current_point')) >= 1 and "http:" in text:
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



