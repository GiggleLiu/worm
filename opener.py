#-*-coding:utf-8-*-

import urllib2,cookielib,cgi,requests,json
import pdb

from setting import BROWSER_HEAD

__all__=['MyBrowser']

class MyBrowser(object):
    # head: dict of header
    def __init__(self):
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.opener.addheaders = BROWSER_HEAD

    def openlink(self,link,encoding=None):
        '''Open a link and get contents.'''
        uop = self.opener.open(link, timeout = 1000)
        data = uop.read()
        _, params = cgi.parse_header(uop.headers.get('Content-Type', ''))
        if encoding is None: encoding = params.get('charset', 'utf-8')
        data=data.decode(encoding=encoding)
        return data

    def request_update(self,link,data,baselink):
        headers={
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Connection':'keep-alive',
        'Cookie':'; '.join(['%s=%s'%(item.name,item.value) for item in self.cookie]),
        'Host':baselink,
        'Referer':baselink,
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/53.0.2785.143 Chrome/53.0.2785.143 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest',
        }
        re=requests.get(link,headers = headers,data=data)
        pdb.set_trace()
        return json.loads(re.text)
