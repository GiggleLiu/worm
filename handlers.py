#-*-coding:utf-8-*-

from lxml import html
import requests,re
from abc import ABCMeta, abstractmethod

from models import *
from utils import inherit_docstring_from

__all__=['get_handler']

class SourceHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self,source):
        self.source=source

    @abstractmethod
    def get_zblist(self,pagecontent):
        '''Get the list of zhong biao xiang mu.
        
        Parameters:
            :pagecontent: str, page content for source page.

        Return:
            list, posts
        '''
        pass

    @abstractmethod
    def get_money(self,pagecontent):
        '''Get the money from detailed page.
        
        Parameters:
            :pagecontent: str, page content for detailed page.
        
        Return:
            float,
        '''
        pass

#for the first source.
class SH1(SourceHandler):
    '''中国政府采购网'''
    @inherit_docstring_from(SourceHandler)
    def get_zblist(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=[e for e in tree.xpath("//ul[@class='ulst']")[0].iter() if e.tag=='li']
        posts=[]
        for li in lis:
            link_elem=li.find('a')
            spans=li.findall('span')
            posts.append(Post(link_elem.text,self.source.baselink+link_elem.get('href'),time=spans[1].text,source_id=self.source.id))
        return posts

    @inherit_docstring_from(SourceHandler)
    def get_money(self,pagecontent):
        tree=html.fromstring(pagecontent)
        ele=tree.xpath(u".//td[contains(text(),'人民币')]")[0]
        res=re.findall(r'(\d+\.?\d*)',ele.text)
        return float(res[0])

def get_handler(source):
    '''
    Get Handler by source.
    '''
    if source.name=='中国政府采购网':
        return SH1(source)
    else:
        raise ValueError
