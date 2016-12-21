#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import requests,re,datetime,time,os,sys
import pdb

sys.path.insert(0,'./')
from utils import quicksave,quickload,beep,load_samplepage,browsepage
from models import get_sources,save_post,get_posts_bysid,get_source
from handlers import get_handler,SourceHandlerB,SourceHandlerA,SourceHandlerC
from opener import MyBrowser

TESTMODE=False

def test_getsource(isource):
    source=get_source(isource)
    handler=get_handler(source)

    if TESTMODE:
        page=load_samplepage(isource)
    else:
        page=handler.browser.openlink(source.baselink)
        quicksave('samples%s/sample_page.dat'%isource,page)
    print 'Get source %s'%handler.source
    return handler,page

def test_list(isource):
    handler=get_handler(get_source(isource))
    page=handler.update()
    if page is not None:
        quicksave('samples%s/sample_page.dat'%isource,page)
    posts=handler.posts

    print 'Posts'
    for i,p in enumerate(handler.posts):
        print p
    print 'Important Posts'
    for i,p in enumerate(handler.important_posts):
        print p
    pdb.set_trace()

def test_browseupdate():
    source=get_source(8)
    handler=get_handler(source)
    page=handler.browser.openlink(source.baselink)
    pdb.set_trace()


if __name__=='__main__':
    test_list(9)
    #test_browseupdate()
