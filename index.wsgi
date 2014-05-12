# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
import sae
import web
import json
import urllib2
import time
import sae.kvdb
from sae.mail import EmailMessage

reload(sys)
sys.setdefaultencoding('utf-8')

APPKEY = '82966982'
APPNAME = os.environ['APP_NAME']

'''
更改下边的参数:
UID:女神微博数字ID
ACCESS_TOKEN：授权码
SECRET: 自己设置的验证密钥，防止赞微博接口被乱用
TOMAIL: 接收提醒的邮箱
smtp相关的是邮件发送服务器，配置方法见各邮箱帮助页
'''
UID = '1649913047'
ACCESS_TOKEN = '2.00tlpW********'
SECRET = 'bWlh****'
TOMAIL = 'user@qq.com'
smtpserver =  'smtp.163.com'
smtpport = '25'
smtpmail = 'user@163.com'
smtppassword = 'passwd'

urls=('/','Index','/like','Like','/setlike','Setlike')

class Index:
    def GET(self):
        web.redirect('http://miantiao.me')
        
class Like:
    def GET(self):
        global UID,ACCESS_TOKEN,APPNAME,SECRET
        req = 'https://api.weibo.com/2/statuses/user_timeline/ids.json?uid={0}&access_token={1}&count=20'.format(UID,ACCESS_TOKEN)
        weiboids = json.loads(urllib2.urlopen(req,timeout=60).read())
        newids = weiboids['statuses']
        kv = sae.kvdb.KVClient()
        oldids = kv.get('weiboids')
        kv.set('weiboids',newids)
        if oldids == None:
            return 'get again!'
        likeids = list(set(newids).difference(set(oldids)))
        for weiboid in likeids:            
            content = 'https://api.weibo.com/2/statuses/show.json?access_token={0}&id={1}'.format(ACCESS_TOKEN,weiboid)
            content = json.loads(urllib2.urlopen(content,timeout=60).read())
            if content.has_key('retweeted_status'):
                content = ''.join([content['text'],'//@',content['retweeted_status']['user']['screen_name'],':',content['retweeted_status']['text']])
            else:
                content = content['text']
            likeurl = 'http://{0}.sinaapp.com/setlike?secert={1}&id={2}'.format(APPNAME,SECRET,weiboid)
            subject = '女神微博更新啦，快去点赞！'
            body = "内容：{0}<br/>一键点赞：<a href='{1}'>{1}</a>".format(content,likeurl)
            self.sendmail(subject,body)            
            time.sleep(1)
        return 'checked'
    def sendmail(self,subject,body):
        global TOMAIL , smtpserver, smtpport, smtpmail, smtppassword
        m = EmailMessage()
        m.to = TOMAIL
        m.subject = subject
        m.html = body
        m.smtp = (smtpserver, smtpport, smtpmail, smtppassword, False)
        m.send()
class Setlike:
    def GET(self):
        global APPKEY,ACCESS_TOKEN,SECRET
        user_data = web.input()
        weiboid = user_data.id
        if user_data.secert==SECRET and weiboid:
            pass
        else:
            return 'secert is wrong or id is null'
        url = 'https://api.weibo.cn/2/like/set_like.json?source={0}&access_token={1}&id={2}'.format(APPKEY,ACCESS_TOKEN,weiboid)
        urllib2.urlopen(url,timeout=60) 
        return 'liked'
    
app = web.application(urls, globals()).wsgifunc() 
application = sae.create_wsgi_app(app)
