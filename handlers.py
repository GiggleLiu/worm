#-*-coding:utf-8-*-

from lxml import html
import requests,re,time,bisect,random
from abc import ABCMeta, abstractmethod
from datetime import datetime,timedelta,date
import pdb

from models import *
from utils import inherit_docstring_from,match_money,load_samplepage,beep
from setting import KEYWORDS_MES,KEYWORDS_ANS,TARGET_MONEY,UPDATE_SPAN,POSTCACHE,TESTMODE,NBEEP

__all__=['get_handler','SourceHandlerA','SourceHandlerB','SourceHandlerC','GHandler','get_groups']

class SourceHandler(object):
    '''
    Souce Handler class.

    Attributes:
        :source: <Source>, source with title and link.
        :status: str, 'ok', 'error'.
        :posts: list, <Post> instances.
        :update_span: int, time interval for updates.
    '''
    __metaclass__ = ABCMeta

    update_span=200
    group=-1
    status='ok'

    def __init__(self,source):
        self.source=source
        self.posts=[]

    @abstractmethod
    def get_list(self,pagecontent):
        '''Get the list of posts.
        
        Parameters:
            :pagecontent: str, page content for source page.

        Return:
            list, posts
        '''
        pass

    @abstractmethod
    def accept(self,post):
        '''
        Decide accept this post or not.
        
        Parameters:
            :post: <Post>,

        Return:
            bool,
        '''
        pass

    def has_post(self,p):
        '''Has post or not.'''
        return any([pi==p for pi in self.posts])

    def add_post(self,post):
        '''add a post for specific source'''
        if self.has_post(post):
            return 0
        pq=self.posts
        print 'Add Post %s'%post
        times=[-p.time for p in pq]
        pos=bisect.bisect_right(times,-post.time)
        pq.insert(pos,post)
        if len(pq)>POSTCACHE:
            pq.pop(-1)
        return 1

    def update(self):
        '''
        Update post information from the source.
        '''
        try:
            page=self.source.get_page() if not TESTMODE else load_samplepage(self.source.id)
            posts=self.get_list(page)
        except:
            raise
            print 'Error: Can not get main page for source %s!'%self.source
            return 0
        try:
            if TESTMODE: posts=[p for p in posts if random.random()>0.4]
            for i,post in enumerate(posts):
                #filter old pages
                if self.has_post(post):
                    continue
                if self.accept(post):
                    info=self.add_post(post)
                    if info: beep(NBEEP)
                    if not TESTMODE:
                        time.sleep(1)
            return 1
        except:
            raise
            print 'Error while processing posts for %s'%self.source
            page=None
            return 0

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
        for p in get_posts_bysid(self.source.id):
            self.add_post(p)


class SourceHandlerA(SourceHandler):
    __metaclass__ = ABCMeta

    group=0
    update_span=UPDATE_SPAN[0]
    status='ok'

    @abstractmethod
    def get_money(self,pagecontent):
        '''Get the money from detailed page.
        
        Parameters:
            :pagecontent: str, page content for detailed page.
        
        Return:
            float,
        '''
        pass

    @inherit_docstring_from(SourceHandler)
    def accept(self,post):
        pagei=post.get_page()
        post.pagecontent=pagei
        post.money=self.get_money(pagei)
        return post.money>=TARGET_MONEY


class SourceHandlerB(SourceHandler):
    __metaclass__ = ABCMeta
    
    group=1
    update_span=UPDATE_SPAN[1]

    @inherit_docstring_from(SourceHandler)
    def accept(self,post):
        '''decide accept this post or not.'''
        return any([k in post.title for k in KEYWORDS_MES])

class SourceHandlerC(SourceHandler):
    __metaclass__ = ABCMeta
    
    group=2
    update_span=UPDATE_SPAN[2]

    @inherit_docstring_from(SourceHandler)
    def accept(self,post):
        return any([k in post.title for k in KEYWORDS_ANS])

################### Groupwise SourceHandler #################

class GHandler(object):
    '''Group handler with update, save and load.'''
    def __init__(self,handlers):
        self.handlers=handlers

    @property
    def posts(self):
        return reduce(lambda x,y:x+y,[h.posts for h in self.handlers])

    def update(self,group=None):
        '''update posts for all sources(in group).'''
        print '###################### UPDATE #######################'
        for h in self.handlers:
            info=h.update()
            if info==0: print 'Can not update posts from source: %s'%self.handlers[i].source

    def save_posts(self,group=None):
        '''save all posts'''
        print '###################### SAVE #######################'
        for h in self.handlers:
            info=h.save()
            if info==0: print 'Can not update posts from source: %s'%self.handlers[i].source

    def load_posts(self,group=None):
        '''load all posts'''
        print '###################### LOAD #######################'
        for h in self.group(group):
            info=h.load()
            if info==0: print 'Can not update posts from source: %s'%self.handlers[i].source

################################# Specific Sources ##############################

class SHA0(SourceHandlerA):
    '''中国政府采购网'''
    status='ok'

    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=[e for e in tree.xpath("//ul[@class='ulst']")[0].iter() if e.tag=='li']
        posts=[]
        for li in lis:
            link_elem=li.find('a')
            spans=li.findall('span')
            t=time.mktime(datetime.strptime(spans[1].text,'%Y-%m-%d %H:%M:%S').timetuple())
            posts.append(Post(link_elem.text,self.source.baselink+link_elem.get('href'),time=t,source_id=self.source.id))
        return posts

    @inherit_docstring_from(SourceHandlerA)
    def get_money(self,pagecontent):
        tree=html.fromstring(pagecontent)
        ele=tree.xpath(u".//td[text()[contains(.,'人民币')]]")[0]
        res=match_money(ele.text)
        return res

class SHA1(SourceHandlerA):
    '''北京财政'''
    status='ok'
    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u"//a[@class='a2']")
        #times=tree.xpath("//td[@width=\"70\"]")
        baselink=self.source.baselink
        while baselink[-1]!='/':
            baselink=baselink[:-1]
        posts=[]
        for li in lis:
            posts.append(Post(li.get('title'),baselink+li.get('href'),time=time.time(),source_id=self.source.id))
        return posts

    @inherit_docstring_from(SourceHandlerA)
    def get_money(self,pagecontent):
        #hard to be implemented
        return 0
        #return match_money(pagecontent)

class SHA2(SourceHandlerA):
    '''广州市政府采购网'''
    status='ok'
    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u"//li[contains(.,'中标')]")
        baselink='http://www.gzg2b.gov.cn'
        posts=[]
        for li in lis:
            try:
                a=li.find('a')
                t=time.mktime(datetime.strptime(li.find('em').text.strip('\r\n '),'%Y-%m-%d %H:%M').timetuple())
                posts.append(Post(a.text.strip('\r\n '),baselink+a.get('href'),time=t,source_id=self.source.id))
            except:
                print 'Decode Fail: %s'%li
        return posts

    @inherit_docstring_from(SourceHandlerA)
    def get_money(self,pagecontent):
        return match_money(pagecontent)

class SHB0(SourceHandlerB):
    '''云财经'''
    status='error'
    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        raise NotImplementedError

class SHB1(SourceHandlerB):
    '''证快讯'''
    status='ok'
    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u".//div[@class='title']")
        posts=[]
        for li in lis:
            try:
                a=li.xpath(u'.//a[@target="_blank"]')[0]
                title=a.get('title') or a.text or a.find('font').text
                t=li.xpath(u".//span[@class='time']")[0].text
                t=datetime.strftime(datetime.now(),'%Y-%m-%d ')+t
                t=time.mktime(datetime.strptime(t,'%Y-%m-%d %H:%M').timetuple())
                post=Post(title,a.get('href'),time=t,source_id=self.source.id)
                if self.accept(post):
                    posts.append(post)
            except:
                raise
                print 'Parsing Error!@B1'
        return posts

class SHB2(SourceHandlerB):
    '''财联社'''
    status='ok'
    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u"//ul[@class='fix']")
        posts=[]
        for li in lis:
            try:
                t,title=[l.text for l in li.findall('li')[:2]]
                t=datetime.strftime(datetime.now(),'%Y-%m-%d ')+t
                t=time.mktime(datetime.strptime(t,'%Y-%m-%d %H:%M').timetuple())
                post=Post(title.strip('\r\n\t '),'',time=t,source_id=self.source.id)
                if self.accept(post):
                    posts.append(post)
            except:
                raise
                print 'Parsing Error!@B2'
        return posts

class SHC1(SourceHandlerC):
    '''
    互动易
    '''
    status='ok'
    def _decode_time(self,t):
        match1=re.match(r'昨天 \d+:\d+',t)
        if match1:
            t=datetime.strftime(date.today()-timedelta(1),'%Y-%m-%d ')+t
            t=time.mktime(datetime.strptime(t,'%Y-%m-%d %H:%M').timetuple())
            return t

        match2=re.match(r'\d+月\d+日 \d+:\d+',t)
        if match2:
            t=time.mktime(datetime.strptime(str(date.today().year)+'-'+t,'%Y-%m月%d日 %H:%M').timetuple())
            return t

    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u".//div[@class='m_feed_detail m_qa']")
        posts=[]
        for li in lis:
            try:
                isans=li.xpath(u".//div[@class='m_feed_info']")[0].find('div').get('class')=='answer_ico'
                if not isans: continue
                user=li.xpath(u".//div[@class='m_feed_face']")[0].find('p').text
                ans=user+': '+li.xpath(u".//div[@class='m_feed_txt']")[0].text
                t=li.xpath(u".//div[@class='m_feed_from']")[0].find('span').text
                t=self._decode_time(t)

                post=Post(title.strip('\r\n\t '),'',time=t,source_id=self.source.id)
                if self.accept(post):
                    posts.append(post)
            except:
                raise
                print 'Parsing Error!@B2'
        return posts

def get_handler(source):
    '''
    Get Handler by source.
    '''
    if source.name=='中国政府采购网':
        return SHA0(source)
    elif source.name=='北京财政':
        return SHA1(source)
    elif source.name=='广州市政府采购网':
        return SHA2(source)
    elif source.name=='云财经':
        return SHB0(source)
    elif source.name=='证快讯':
        return SHB1(source)
    elif source.name=='财联社':
        return SHB2(source)
    else:
        raise ValueError

def get_groups(handlers):
    '''Get all groups.'''
    gs=[[],[],[]]
    for h in handlers:
        gs[h.group].append(h)
    return [GHandler(g) for g in gs]
