#-*-coding:utf-8-*-
'''
Data scraping
'''

from lxml import html
import requests,re,datetime,time,os,threading
from numpy import *
import pdb

from utils import quicksave,quickload,beep,load_samplepage
from models import get_sources,save_post,get_posts
from handlers import get_handler
from setting import TESTMODE,NBEEP,UPDATE_SPAN

class Worm(object):
    '''
    Worm continuously fetch datas.
    
    Attibutes:
        :npost: int, maximum number of posts alive.
        :pages: list, the main page for sources.
        :posts: list, <Post> instances.

        :handlers: list, <SourceHandler> instances.
        :_stop_event: <threading.Event> instance, that control the listening thread.
        :is_listening(read only): bool,
    '''
    handlers=[get_handler(source) for source in get_sources()]

    def __init__(self,npost=100):
        self.npost=npost
        self._stop_event=threading.Event()
        nh=len(self.handlers)
        self.pages=[None]*nh
        #list items are posts in a queue of length 100
        self.posts=[]
        self.stop_listen()
        self.update_all()

    @property
    def is_listening(self):
        return not self._stop_event.isSet()

    def get_handler_bysid(self,id):
        '''Get the handler by id of source.'''
        for i,h in enumerate(self.handlers):
            if h.source.id==id:
                return i

    def has_post(self,title):
        '''Has post or not.'''
        return any([p.title==title for p in self.posts])

    def addpost(self,post):
        '''add a post for specific source'''
        if self.has_post(post.title):
            return 0
        pq=self.posts
        print 'Add Post %s'%post
        times=[-p.get_time() for p in pq]
        pos=searchsorted(times,-post.get_time())
        pq.insert(pos,post)
        if len(pq)>self.npost:
            pq.pop(-1)
        return 1

    def update_all(self):
        '''update posts for all sources.'''
        for i in xrange(len(self.handlers)):
            info=self.update(i)
            if info==0: print 'Can not update posts from source: %s'%self.handlers[i].source

    def update(self,n):
        '''Update from i-th source.'''
        h=self.handlers[n]
        try:
            page=h.source.get_page() if not TESTMODE else load_samplepage()
            posts=h.get_zblist(page)
            if TESTMODE: posts=[p for p in posts if random.random()>0.4]
            for i,post in enumerate(posts):
                #filter old pages
                if self.has_post(post.title):
                    continue
                pagei=post.get_page() if not TESTMODE else load_samplepage(i)
                post.pagecontent=pagei
                post.money=h.get_money(pagei)
                info=self.addpost(post)
                if info and self.pages[n] is not None: beep(NBEEP)
                if not TESTMODE:
                    time.sleep(1)
            self.pages[n]=page
            succ=1
        except:
            raise
            page=None
            succ=0
        return succ

    def save_posts(self):
        '''Save all posts.'''
        for p in self.posts:
            try:
                save_post(p)
            except:
                print 'skip existing post.'

    def load_posts(self):
        '''Load posts stored in database.'''
        self.posts=[]
        for p in get_posts():
            self.addpost(p)

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

