# -*- coding: utf-8 -*-
#!/usr/bin/env python
#version:0.1
#auther:ccbikai
import os
import sae
import web
import json
import urllib2
import time
import sae.kvdb

APPKEY = '82966982'

'''
更改下边的参数:
UID:女神微博数字ID
ACCESS_TOKEN：授权码。
'''
UID = '1649913047'
ACCESS_TOKEN = '2.00tlp***********'

urls=('/','Index','/like','Likefordear')

class Index:
    def GET(self):
        web.redirect('http://miantiao.me')
        
class Likefordear:
    def GET(self):
        global UID,APPKEY,ACCESS_TOKEN
        req = 'https://api.weibo.com/2/statuses/user_timeline/ids.json?uid={0}&appkey={1}&access_token={2}&count=20'.format(UID,APPKEY,ACCESS_TOKEN)
        weiboids = json.loads(urllib2.urlopen(req,timeout=60).read())
        newids = weiboids['statuses']
        kv = sae.kvdb.KVClient()
        oldids = kv.get('weiboids')
        kv.set('weiboids',newids)
        if oldids == None:
            return 'get again!'
        likeids = list(set(newids).difference(set(oldids)))
        for weiboid in likeids:
            url = 'https://api.weibo.cn/2/like/set_like.json?source={0}&access_token={1}&id={2}'.format(APPKEY,ACCESS_TOKEN,weiboid)
            like = urllib2.urlopen(url,timeout=60)
            time.sleep(2)
        return 'liked'

app = web.application(urls, globals()).wsgifunc() 
application = sae.create_wsgi_app(app)
