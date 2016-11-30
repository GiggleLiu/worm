#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import requests,re,datetime,time,os,sys
from numpy import *
import pdb

sys.path.insert(0,'./')
from utils import quicksave,quickload,beep,load_samplepage
from models import get_sources,save_post,get_posts_bysid
from handlers import get_handler

TESTMODE=True

sources=get_sources()
source=sources[0]
handler=get_handler(source)

if TESTMODE:
    page=load_samplepage()
else:
    page=source.get_page()
    quicksave('samples/sample_page.dat',page)

posts=handler.get_zblist(page)
for i,p in enumerate(posts):
    if TESTMODE:
        pagei=load_samplepage(i)
    else:
        pagei=p.get_page()
        time.sleep(1)
        quicksave('samples/sample_page_%s.dat'%i,pagei)
    p.money=handler.get_money(pagei)
    print save_post(p)

for i,p in enumerate(posts):
    print p
    #print p.get_time()
    #pdb.set_trace()

