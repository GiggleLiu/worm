#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import requests,re,datetime,time,os,sys
import pdb

sys.path.insert(0,'./')
from utils import quicksave,quickload,beep,load_samplepage
from models import get_sources,save_post,get_posts_bysid
from handlers import get_handler,SourceHandlerB,SourceHandlerA

TESTMODE=False

def test_getsource(isource):
    sources=get_sources()
    source=[source for source in sources if source.id==isource][0]
    handler=get_handler(source)

    if TESTMODE:
        page=load_samplepage(isource)
    else:
        page=source.get_page()
        quicksave('samples%s/sample_page.dat'%isource,page)
    return handler,page

def test_getzb(isource):
    handler,page=test_getsource(isource)
    if not isinstance(handler,SourceHandlerA):
        raise ValueError
    handler.update()
    posts=handler.posts

    for i,p in enumerate(posts):
        print p

def test_getmes(isource):
    handler,page=test_getsource(isource)
    if not isinstance(handler,SourceHandlerB):
        raise ValueError
    handler.update()
    posts=handler.posts

    for i,p in enumerate(posts):
        print p

if __name__=='__main__':
    test_getzb(3)
    #test_getmes(6)
