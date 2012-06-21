# -*- coding: utf-8 -*-
'''
Created on 2012-6-21

@author: shellshy
'''
from django.conf import settings

def getTags():
    tags = settings.TAG.keys()
    return tags

def getUserList(tag):
    uids = settings.TAG.smembers(tag)
    return uids

#获取用户标签
def getUserTags(uid):
    result = []
    tags = getTags()
    for tag in tags:
        uids = getUserList(tag)
        if uid in uids:
            result.append(tag)
    
    return result

#获取用户标签相关的用户的uid列表
def getRelateUsers(uid):
    result = set()
    tags = getTags()
    for tag in tags:
        uids = getUserList(tag)
        if uid in uids:
            result = result | uids
    
    result = result - uid
    return result

#通过标签获取微博的id集合
def getWeiboIdByTag(tag):
    ids = settings.WEIBO.smembers(tag + '_weiboids')
    return ids

#通过用户id获取微博的数据
def getWeiboIdByUid(uid):
    ids = settings.WEIBO.smembers(uid + '_weiboids')
    return ids

#通过微博的id获取微博的详细信息
def getWeiboById(wid):
    weibo = settings.WEIBO.smembers(wid)
    return weibo