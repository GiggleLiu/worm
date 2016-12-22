#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import requests,re,datetime,time,os,sys
import pdb

sys.path.insert(0,'./')
from utils import beep
from models import get_sources
from handlers import *
from opener import MyBrowser

TESTMODE=False

def test_refresh(isource):
    handler=get_handler(get_sources[isource-1])
    page=handler.refresh()
    posts=handler.posts

    print 'Posts'
    for i,p in enumerate(handler.posts):
        print p
    print 'Important Posts'
    for i,p in enumerate(handler.important_posts):
        print p
    pdb.set_trace()

def test_update(isource):
    handler=get_handler(get_sources[isource-1])
    page=handler.update()
    posts=handler.posts

    print 'Posts'
    for i,p in enumerate(handler.posts):
        print p
    print 'Important Posts'
    for i,p in enumerate(handler.important_posts):
        print p
    pdb.set_trace()

def test_listen(isource):
    handler=get_handler(get_sources[isource-1])
    page=handler.update()
    posts=handler.posts

    print 'Posts'
    for i,p in enumerate(handler.posts):
        print p
    print 'Important Posts'
    for i,p in enumerate(handler.important_posts):
        print p
    pdb.set_trace()

def test_browseupdate():
    source=get_sources[7]
    handler=get_handler(source)
    page=handler.browser.openlink(source.baselink)
    pdb.set_trace()

if __name__=='__main__':
    test_refresh(7)
    #test_browseupdate()
