# -*- coding: utf-8 -*-
'''
Created on 2012-6-21

@author: shellshy
'''
import redis,json
TAG = redis.StrictRedis(host='localhost', port=6379, db=0)
WEIBO = redis.StrictRedis(host='localhost', port=6379, db=0)

def getTags():
    tags = TAG.keys()
    return tags

def getUserList(tag):
    uids = TAG.smembers(tag)
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
    result = []
    tags = getTags()
    for tag in tags:
        uids = getUserList(tag)
        if uid in uids:
            result = result + uids
    
    result = set(result)
    result = result - uid
    return result

#通过标签获取微博的id集合
def getWeiboIdByTag(tag):
    ids = WEIBO.smembers(tag + '_weiboids')
    return ids

#通过用户id获取微博的数据
def getWeiboIdByUid(uid):
    ids = WEIBO.smembers(uid + '_weiboids')
    return ids

#通过微博的id获取微博的详细信息
def getWeiboById(wid):
    weibo = WEIBO.get("weiboid_" + wid)
    #weibo = json.loads(weibo)
    return weibo