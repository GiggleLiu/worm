#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import requests,re,datetime,time,os,sys
import pdb

sys.path.insert(0,'./')
from utils import *
from models import get_sources,save_post,get_posts_bysid
from handlers import get_handler


def test_matchmoney():
    cases=['采购预算：人民币4344万元',
            '中标金额：3627800元',
            '贰佰叁拾捌万贰仟陆佰柒拾元整   ￥2,382,670.00',
            ]
    ms=[4344,362.78,238.267]

    for case,m in zip(cases,ms):
        assert(match_money(case)==m)

if __name__=='__main__':
    test_matchmoney()
