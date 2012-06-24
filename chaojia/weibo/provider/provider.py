# -*- coding: utf-8 -*-
'''
Created on 2012-6-21

@author: shellshy
'''
import redis,json
TAG = redis.StrictRedis(host='localhost', port=6379, db=0)
WEIBO = redis.StrictRedis(host='localhost', port=6379, db=0)
ADMIN = redis.StrictRedis(host='localhost', port=6379, db=9)

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
    return weibo

#用户获取置顶的weibo数据
def getZhiDingWid(uid):
    zhiding_wids = ADMIN.get['zhiding'].values()#获取置顶的微博id    
    keys = ADMIN.keys()#三个小时用户转发过的微博wid
    count = 0
    result = []
    for wid in zhiding_wids:
        if count > 3:
            break;
        
        if 'zf_' + uid + '_' + str(wid) not in keys:
            count = count + 1
            result.append(wid)#添加置顶的微博id
    
    return result

#过滤3小时内已经转发过的微博
def filterZF(uid,wids):    
    result = []
    keys = ADMIN.keys()#三个小时用户转发过的微博wid
    for wid in wids:
        if 'zf_' + uid + '_' + str(wid) not in keys:
            result.append(wid)
    return result