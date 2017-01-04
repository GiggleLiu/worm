#-*-coding:utf-8-*-

import cgi,http.cookiejar
from six.moves.urllib.request import build_opener,HTTPCookieProcessor
import pdb

from setting import BROWSER_HEAD

__all__=['MyBrowser']

class MyBrowser(object):
    # head: dict of header
    def __init__(self):
        self.cookie = http.cookiejar.CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cookie))
        self.opener.addheaders = BROWSER_HEAD

    def openlink(self,link,encoding=None):
        '''Open a link and get contents.'''
        uop = self.opener.open(link, timeout = 1000)
        data = uop.read()
        _, params = cgi.parse_header(uop.headers.get('Content-Type', ''))
        if encoding is None: encoding = params.get('charset', 'utf-8')
        data=data.decode(encoding=encoding)
        return data
