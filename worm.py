#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import pdb

from models import get_sources
from handlers import get_handler

class Worm(object):
    '''
    Worm continuously fetch datas.
    
    Attibutes:

        :handlers: list, <SourceHandler> instances.
    '''
    def __init__(self):
        #get handlers
        handlers=[get_handler(source) for source in get_sources()]
        handlers=[h for h in handlers if h.source.status=='ok']
        self.handlers=handlers

    def get_handler_bysid(self,id):
        '''Get the handler by id of source.'''
        for i,h in enumerate(self.handlers):
            if h.source.id==id:
                return h
        return -1

    def do(self,command,isource=None):
        '''
        Do command on specific source.

        Parameters:
            :command: str, one of 'update'/'refresh'/'listen'/'stop_listen'
            :isource: int/list/None, source id/list of source ids/all sources.
        '''
        if isource is None:
            handlers=self.handlers
        else:
            if not hasattr(isource,'__iter__'): isource=[isource]
            handlers=[self.get_handler_bysid(x) for x in isource]
        for h in handlers:
            if h is -1:
                print 'Can not find specific handler %s.'%isource
            else:
                getattr(h,command)()

    def get_listeners(self):
        '''Get all listeners.'''
        return [h for h in self.handlers if h.is_listening]

    def print_stat(self):
        '''Get summary information.'''
        print 'Summary '+'-'*72
        for h in self.handlers:
            print h.__str__().decode('utf-8')
        print '-'*80
        print 'All %s sources.'%len(self.handlers)

    def get_posts(self,maxN,isource=None,kw=None,important=True):
        '''Get posts.'''
        if isource is None:
            handlers=self.handlers
        else:
            if not hasattr(isource,'__iter__'): isource=[isource]
            handlers=[self.get_handler_bysid(x) for x in isource]
        posts=[]
        for ih,h in enumerate(handlers):
            if h is -1:
                print 'Can not find handler for source %s.'%isource[ih]
            else:
                posts.extend(h.posts)
        if kw is not None:
            posts=filter(lambda p:kw in p.title,posts)
        if important:
            posts=filter(lambda p:p.is_important,posts)
        posts=sorted(posts,key=lambda p:p.time)
        return posts[-maxN:]
