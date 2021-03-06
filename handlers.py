#-*-coding:utf-8-*-


from lxml import html
import time,bisect,random,json,sched
from abc import ABCMeta, abstractmethod
import pdb

from models import *
from utils import inherit_docstring_from,match_money,beep
from setting import KEYWORDS_MES,KEYWORDS_ANS,TARGET_MONEY,POSTCACHE,NBEEP,SOURCE_CONFIG,ALERT_MODE
from opener import MyBrowser

__all__=['get_handler','RefreshHandler','JsonHandler','JRHandler','WSHandler','DummyHandler']

class SourceHandler(object, metaclass=ABCMeta):
    '''
    Souce Handler class.

    Attributes:
        :source: <Source>, source with title and link.
        :posts: list, <Post> instances.
        :is_listening(read only): bool,
    '''

    def __init__(self,source):
        self.source=source
        #initialize post cache
        self.posts=[]
        #the opener
        self.browser=MyBrowser()
        #listening,
        self._job=None

    def __str__(self):
        return '%s\n\tlistening(every %ss): %s\n\tnumber of posts: %s'%(self.source,\
                self.source.update_span,'yes' if self.is_listening else 'no',len(self.posts))

    @property
    def important_posts(self):
        '''Get important posts.'''
        return [p for p in self.posts if p.is_important]

    @property
    def is_listening(self):
        '''bool, is listening or not.'''
        return self._job is not None and not (self._job.next_run_time is None or self._job.pending)

    ##################### Post management ################
    @abstractmethod
    def _extract_list(self,pagecontent):
        '''Get the list of posts.
        
        Parameters:
            :pagecontent: str, page content for source page.

        Return:
            list, posts
        '''
        pass

    def is_important(self,post):
        '''
        Decide this post is important or not (by group).
        
        Parameters:
            :post: <Post>,

        Return:
            bool,
        '''
        if self.source.group==0:
            if post.pagecontent=='' and post.money==-1:
                pagei=self.browser.openlink(post.link)
                post.pagecontent=pagei
                post.money=self.get_money(pagei)
            return post.money>=TARGET_MONEY
        elif self.source.group==1:
            return any([k in post.title for k in KEYWORDS_MES])
        elif self.source.group==2:
            return any([k in post.title for k in KEYWORDS_ANS])
        elif self.source.group==-1:  #dummy group
            print('Is Important -> %s'%post)
            return random.random()>0.5
        else:
            raise ValueError

    def has_post(self,p):
        '''Has post or not.'''
        return any([pi==p for pi in self.posts])

    def add_post(self,post):
        '''
        Add a post for specific source

        Parameters:
            :post: list/<Post>,
        '''
        if hasattr(post,'__iter__'):
            return any([self.add_post(p) for p in post])
        if self.has_post(post):
            return 0
        #insert the post by time
        pq=self.posts
        times=[-p.time for p in pq]
        pos=bisect.bisect_right(times,-post.time)
        pq.insert(pos,post)
        if len(pq)>POSTCACHE:
            pq.pop(-1)
        #classify posts and tell the user
        if self.is_important(post):
            post.is_important=True
        alert_post(post)
        return 1

    ####################### fetching data #################
    @abstractmethod
    def update(self):
        '''
        Update post information from the source.
        '''
        pass

    def refresh(self):
        '''
        Refresh the list page and get lists.
        '''
        page=self.browser.openlink(self.source.baselink)
        posts=self._extract_list(page)
        self.add_post(posts)
        return page

    def _updator(self):
        print('Listen: Update Source %s'%self.source.name)
        self.update()

    ######################## listening #################

    def listen(self,s):
        '''s is a scheduler'''
        if self.is_listening:
            return self._job
        elif self._job is not None:
            print('Listening source %s.'%self.source.id)
            self._job.resume()
            return self._job
        else:
            #generate a new thread if first listening.
            print('Listening source %s.'%self.source.id)
            job=s.add_job(self._updator,'interval',seconds=self.source.update_span,misfire_grace_time=10)
            self._job=job
            return job

    def stop_listen(self):
        '''Stop an listening even.'''
        if not self.is_listening:
            return self._job
        else:
            print('Stop listening source %s.'%self.source.id)
            self._job.pause()
            return self._job

class DummyHandler(SourceHandler):
    '''Dummy Handler.'''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        ipost=random.randint(0,100000000)
        posts=[Post('Title-%s'%ipost,link='http://127.0.0.1/',time=time.time(),source_id=-1) for i in range(random.randint(0,15))]
        res=[p for p in posts]
        print('Fetch list, get %s posts.'%len(res))
        return res

class RefreshHandler(SourceHandler, metaclass=ABCMeta):
    @inherit_docstring_from(SourceHandler)
    def update(self):
        self.refresh()

class JsonHandler(SourceHandler, metaclass=ABCMeta):
    pass
    
class JRHandler(SourceHandler, metaclass=ABCMeta):
    '''Json + Refresh type update.'''
    @inherit_docstring_from(SourceHandler)
    def update(self):
        if self.need_update():
            self.refresh()

class WSHandler(SourceHandler, metaclass=ABCMeta):
    '''Web Socket type update.'''

################################# Specific Sources ##############################

class SHA0(RefreshHandler):
    '''中国政府采购网'''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=[e for e in tree.xpath("//ul[@class='ulst']")[0].iter() if e.tag=='li']
        posts=[]
        for li in lis[::-1]:
            link_elem=li.find('a')
            posts.append(Post(link_elem.text,self.source.baselink+link_elem.get('href'),time=time.time(),source_id=self.source.id))
        return posts

    def get_money(self,pagecontent):
        tree=html.fromstring(pagecontent)
        ele=tree.xpath(".//td[text()[contains(.,'人民币')]]")
        if len(ele)>0:
            res=match_money(ele[0].text)
            return res or 0
        else:
            return 0

class SHA1(RefreshHandler):
    '''北京财政'''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath("//a[@class='a2']")
        #times=tree.xpath("//td[@width=\"70\"]")
        baselink=self.source.baselink
        while baselink[-1]!='/':
            baselink=baselink[:-1]
        posts=[]
        for li in lis[::-1]:
            posts.append(Post(li.get('title'),baselink+li.get('href'),time=time.time(),source_id=self.source.id))
        return posts

    def get_money(self,pagecontent):
        return match_money(pagecontent)

class SHA2(RefreshHandler):
    '''广州市政府采购网'''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath("//li[contains(.,'中标')]")
        baselink='http://www.gzg2b.gov.cn'
        posts=[]
        for li in lis[::-1]:
            try:
                a=li.find('a')
                posts.append(Post(a.text.strip('\r\n '),baselink+a.get('href'),time=time.time(),source_id=self.source.id))
            except:
                print('Decode Fail: %s'%li)
        return posts

    def get_money(self,pagecontent):
        return match_money(pagecontent)

class SHB0(WSHandler):
    '''云财经'''
    def update(self):
        text=self.browser.openlink('ws://push.yuncaijing.com:9503/')
        js=json.loads(text)
        self.ctime=int(time.time())-10
        if js==10364: return 0
        posts=[Post(d['content'],self.source.baselink,time=time.time()) for d in js['data']]
        self.add_post(posts)
        return 1

    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        raise NotImplementedError

class SHB1(RefreshHandler):
    '''证快讯'''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(".//div[@class='title']")
        posts=[]
        for li in lis[::-1]:
            try:
                a=li.xpath('.//a[@target="_blank"]')[0]
                title=a.get('title') or a.text or a.find('font').text
                post=Post(title,a.get('href'),time=time.time(),source_id=self.source.id)
                posts.append(post)
            except:
                print('Parsing Error! %s'%self.source)
        return posts

class SHB2(JsonHandler):
    '''财联社'''
    def __init__(self,*args,**kwargs):
        self.ctime=int(time.time())-3600
        super(SHB2,self).__init__(*args,**kwargs)

    def update(self):
        text=self.browser.openlink('http://www.cailianpress.com/v2/article/get_roll?type=-1&staid=%s&count=20&flow=1&_=%s'%(self.ctime,round(time.time()*1000)))
        js=json.loads(text)
        if js['errno']!=0:  #has data
            return
        self.ctime=int(js['previous_cursor'])
        posts=[Post(d['content'],self.source.baselink,time=time.time(),source_id=self.source.id) for d in js['data']]
        self.add_post(posts)
        return 1

    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath("//ul[@class='fix']")
        posts=[]
        for li in lis[::-1]:
            try:
                title=li.findall('li')[1].text.strip('\r\n\t ')
                post=Post(title,self.source.baselink,time=time.time(),source_id=self.source.id)
                posts.append(post)
            except:
                print('Parsing Error! %s'%self.source)
        return posts

class SHC0(RefreshHandler):
    '''
    互动易
    '''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(".//div[@class='answerBox']")
        posts=[]
        for li in lis[::-1]:
            try:
                user=li.xpath(".//a[@class='blue1']")[0].text
                content=li.xpath(".//a[@class='cntcolor']")[0].text
                title=user+': '+content.strip('\r\n\t ')
                post=Post(title,self.source.baselink,time=time.time(),source_id=self.source.id)
                posts.append(post)
            except:
                print('Parsing Error! %s'%self.source)
        return posts

class SHC1(RefreshHandler):
    '''
    上证e互动
    '''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(".//div[@class='m_feed_detail m_qa']")
        posts=[]
        for li in lis[::-1]:
            try:
                userl=li.xpath(".//a[@class='ansface']")
                if len(userl)==0: continue
                ans=userl[0].get('title')+': '+li.xpath(".//div[@class='m_feed_txt']")[0].text.strip('\r\n\t ')
                post=Post(ans,self.source.baselink,time=time.time(),source_id=self.source.id)
                posts.append(post)
            except:
                print('Parsing Error! %s'%self.source)
        return posts

class SHC2(JRHandler):
    '''
    淘财经
    '''
    def __init__(self,*args,**kwargs):
        self.ctime=int(time.time())-10
        self.pid=0  #current post_id.
        super(SHC2,self).__init__(*args,**kwargs)

    def need_update(self):
        text=self.browser.openlink('http://www.taoguba.com/recent_post.id?%s'%(self.ctime*1000))
        js=json.loads(text)
        self.ctime=int(time.time())-10
        if not isinstance(js,int): return 0
        if self.pid==0:
            self.pid=js
            return False
        elif js>self.pid:
            self.pid=js
            return True
        else:
            self.pid=js
            return False

    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(".//article[@class='excerpt excerpt-nothumbnail']")
        posts=[]
        for li in lis[::-1]:
            try:
                ai=li.xpath('.//h2')[0].find('a')
                title,link=ai.text.strip('\r\n\t '),ai.get('href')
                post=Post(title,link,time=time.time(),source_id=self.source.id)
                posts.append(post)
            except:
                print('Parsing Error! %s'%self.source)
        return posts

class SHC3(RefreshHandler):
    '''
    淘股吧
    '''
    @inherit_docstring_from(SourceHandler)
    def _extract_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(".//div[@class='wonder']")
        posts=[]
        for li in lis[1:][::-1]:
            try:
                ai=li.xpath(".//a[@class='wonderLink']")[0]
                title,link=ai.text.strip('\r\n\t '),ai.get('href')
                post=Post(title,link,time=time.time(),source_id=self.source.id)
                posts.append(post)
            except:
                print('Parsing Error! %s'%self.source)
        return posts

def get_handler(source):
    '''
    Get Handler by source.
    '''
    if source.name=='中国政府采购网-PPP':
        cls=SHA0
    elif source.name=='北京财政':
        cls=SHA1
    elif source.name=='广州市政府采购网':
        cls=SHA2
    elif source.name=='云财经':
        cls=SHB0
    elif source.name=='证快讯':
        cls=SHB1
    elif source.name=='财联社':
        cls=SHB2
    elif source.name=='互动易':
        cls=SHC0
    elif source.name=='上证e互动':
        cls=SHC1
    elif source.name=='淘财经':
        cls=SHC2
    elif source.name=='淘股吧':
        cls=SHC3
    elif source.name=='中国政府采购网-中央标':
        cls=SHA0
    elif source.name=='中国政府采购网-地方标':
        cls=SHA0
    elif source.name=='未知源':
        cls=DummyHandler
    else:
        raise ValueError
    return cls(source)

def alert_post(post):
    '''Alert user about new post.'''
    alerts=ALERT_MODE[1 if post.is_important else 0]
    for mode in alerts:
        if mode=='beep':
            beep(NBEEP)
        elif mode=='print':
            print('Add New Post -> %s'%post)
