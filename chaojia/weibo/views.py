# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from provider import provider 

def weibo_home(request):
    tags = provider.getUserTags('1')
    wids = set()
    for tag in tags:
        result = provider.getWeiboIdByTag(tag)
        wids = wids | result
        
    weibos = []
    for wid in wids:
        weibo = provider.getWeiboById(wid)
        weibos.append(weibo)
    
    return HttpResponse(weibos)