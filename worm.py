#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import requests,re,datetime,time,os,threading
import random
import pdb

from utils import quicksave,quickload,beep,load_samplepage
from models import get_sources,save_post,get_posts
from handlers import get_handler,get_groups
from setting import TESTMODE,NBEEP,UPDATE_SPAN

class Worm(object):
    '''
    Worm continuously fetch datas.
    
    Attibutes:

        :groups: list, <GSource> instances.
        :_stop_event: <threading.Event> instance, that control the listening thread.
        :is_listening(read only): bool,
    '''
    def __init__(self,npost=100):
        self.npost=npost
        self._stop_event=threading.Event()
        nh=len(self.handlers)
        #list items are posts in a queue of length 100
        self.stop_listen()
        #get groups of handlers
        handlers=[get_handler(source) for source in get_sources()]
        handlers=[h for h in handlers in h.status=='ok']
        self.groups=get_groups(handlers)
        self.update_all()

    @property
    def is_listening(self):
        return not self._stop_event.isSet()

    def get_handler_bysid(self,id):
        '''Get the handler by id of source.'''
        for i,h in enumerate(self.handlers):
            if h.source.id==id:
                return i

    def listen(self):
        ''''''
        if self.is_listening:
            print 'Already listening.'
            return 0
        self._stop_event.clear()

        def updator():
            while True:
                if not self.is_listening:
                    break
                else:
                    time.sleep(UPDATE_SPAN)
                    self.update_all()
        t=threading.Thread(target=updator,args=())
        t.daemon=True
        t.start()
        self.thread=t
        return 1

    def stop_listen(self):
        '''Stop an listening even.'''
        self._stop_event.set()
