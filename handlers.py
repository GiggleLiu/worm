#-*-coding:utf-8-*-

from lxml import html
import requests,re,time,bisect,random,json
from abc import ABCMeta, abstractmethod
from datetime import datetime,timedelta,date
import pdb

from models import *
from utils import inherit_docstring_from,match_money,load_samplepage,beep
from setting import KEYWORDS_MES,KEYWORDS_ANS,TARGET_MONEY,UPDATE_SPAN,POSTCACHE,TESTMODE,NBEEP
from opener import MyBrowser

__all__=['get_handler','SourceHandlerA','SourceHandlerB','SourceHandlerC','GHandler','get_groups','DummyHandler']

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
        self.browser=MyBrowser()

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
    def is_important(self,post):
        '''
        Decide this post is important or not.
        
        Parameters:
            :post: <Post>,

        Return:
            bool,
        '''
        pass

    @property
    def important_posts(self):
        '''Get important posts.'''
        return filter(self.is_important,self.posts)

    def alert(self,post):
        '''Alert user about new post.'''
        if self.is_important(post):
            post.is_important=True
            beep(NBEEP)
            print '[Important] Add New Post -> %s'%post
        else:
            print 'Add New Post -> %s'%post

    def has_post(self,p):
        '''Has post or not.'''
        return any([pi==p for pi in self.posts])

    def add_post(self,post):
        '''add a post for specific source'''
        if self.has_post(post):
            return 0
        pq=self.posts
        times=[-p.time for p in pq]
        pos=bisect.bisect_right(times,-post.time)
        pq.insert(pos,post)
        if len(pq)>POSTCACHE:
            pq.pop(-1)
        return 1

    def update(self,alert=False):
        '''
        Update post information from the source.
        '''
        try:
            if TESTMODE:
                page=load_samplepage(self.source.id)
            else:
                page=self.browser.openlink(self.source.baselink)
            posts=self.get_list(page)
        except:
            raise
            print 'Error: Can not get main page for source %s!'%self.source
            return None
        try:
            if TESTMODE: posts=[p for p in posts if random.random()>0.4]
            for i,post in enumerate(posts):
                #filter old pages
                if self.has_post(post):
                    continue
                info=self.add_post(post)
                if info and alert: self.alert(post)
            return page
        except:
            raise
            print 'Error while processing posts for %s'%self.source
            return None

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


class DummyHandler(SourceHandler):
    '''Dummy Handler.'''
    @inherit_docstring_from(SourceHandler)
    def is_important(self,post):
        print 'Is Important -> %s'%post
        return random.random()>0.5

    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        ipost=random.randint(0,100000000)
        posts=[Post('Title-%s'%ipost,link='http://127.0.0.1/',time=time.time(),source_id=-1) for i in xrange(random.randint(0,15))]
        res=[p for p in posts]
        print 'Fetch list, get %s posts.'%len(res)
        return res

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
    def is_important(self,post):
        if post.pagecontent=='':
            pagei=self.browser.openlink(post.link)
            post.pagecontent=pagei
            post.money=self.get_money(pagei)
        return post.money>=TARGET_MONEY


class SourceHandlerB(SourceHandler):
    __metaclass__ = ABCMeta
    
    group=1
    update_span=UPDATE_SPAN[1]

    @inherit_docstring_from(SourceHandler)
    def is_important(self,post):
        return any([k in post.title for k in KEYWORDS_MES])

class SourceHandlerC(SourceHandler):
    __metaclass__ = ABCMeta
    
    group=2
    update_span=UPDATE_SPAN[2]

    @inherit_docstring_from(SourceHandler)
    def is_important(self,post):
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
    status='error'   #reason, no uniform money format.
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
        return match_money(pagecontent)

class SHA2(SourceHandlerA):
    '''广州市政府采购网'''
    status='error'   #reason, no uniform money format.
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
        pdb.set_trace()
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
                posts.append(post)
            except:
                raise
                print 'Parsing Error!@B1'
        return posts

class SHB2(SourceHandlerB):
    '''财联社'''
    status='ok'
    def __init__(self,*args,**kwargs):
        self.ctime=str(int(time.time())-3600)
        super(SHB2,self).__init__(*args,**kwargs)

    def update(self):
        text=self.browser.openlink('http://www.cailianpress.com/v2/article/get_roll?type=-1&staid=%s&count=20&flow=1&_=%s'%(self.ctime,round(time.time()*1000)))
        js=json.loads(text)
        if js['errno']!=0:  #has data
            return
        self.ctime=d['previous_cursor']
        posts=[Post(d['content'],'',time=int(d['time']),source_id=self.source.id) for d in js['data']]
        pdb.set_trace()
        return res

    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        raise NotImplementedError()
        #tree=html.fromstring(pagecontent)
        #lis=tree.xpath(u"//ul[@class='fix']")
        #posts=[]
        #for li in lis:
        #    try:
        #        t,title=[l.text for l in li.findall('li')[:2]]
        #        t=datetime.strftime(datetime.now(),'%Y-%m-%d ')+t
        #        t=time.mktime(datetime.strptime(t,'%Y-%m-%d %H:%M').timetuple())
        #        post=Post(title.strip('\r\n\t '),'',time=t,source_id=self.source.id)
        #        posts.append(post)
        #    except:
        #        raise
        #        print 'Parsing Error!@B2'
        #return posts

class SHC0(SourceHandlerC):
    '''
    互动易
    '''
    status='ok'
    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u".//div[@class='answerBox']")
        posts=[]
        for li in lis:
            try:
                user=li.xpath(u".//a[@class='blue1']")[0].text
                content=li.xpath(u".//a[@class='cntcolor']")[0].text
                title=user+': '+content.strip('\r\n\t ')
                t=li.xpath(u".//a[@class='date']")[0].text.strip('\r\n\t ')
                t=time.mktime(datetime.strptime(t.encode('utf-8'),'%Y年%m月%d日 %H:%M').timetuple())

                post=Post(title,'',time=t,source_id=self.source.id)
                posts.append(post)
            except:
                raise
                print 'Parsing Error!@B2'
        return posts

class SHC1(SourceHandlerC):
    '''
    上证e互动
    '''
    status='ok'
    def _decode_time(self,t):
        if isinstance(t,unicode):t=t.encode('utf-8')
        match1=re.match(r'昨天 (\d+:\d+)',t)
        if match1:
            t=datetime.strftime(date.today()-timedelta(1),'%Y-%m-%d ')+match1.group(1)
            t=time.mktime(datetime.strptime(t,'%Y-%m-%d %H:%M').timetuple())
            return t

        match2=re.match(r'\d+月\d+日 \d+:\d+',t)
        if match2:
            t=time.mktime(datetime.strptime(str(date.today().year)+'-'+t,'%Y-%m月%d日 %H:%M').timetuple())
            return t

        match3=re.match(r'(\d+)小时前',t)
        if match3:
            t=time.mktime((datetime.now()-timedelta(int(match3.group(1))/24.)).timetuple())
            return t

    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u".//div[@class='m_feed_detail m_qa']")
        posts=[]
        for li in lis:
            try:
                userl=li.xpath(u".//a[@class='ansface']")
                if len(userl)==0: continue
                ans=userl[0].get('title')+': '+li.xpath(u".//div[@class='m_feed_txt']")[0].text.strip('\r\n\t ')
                t=li.xpath(u".//div[@class='m_feed_from']")[0].find('span').text
                t=self._decode_time(t)
                post=Post(ans,'',time=t,source_id=self.source.id)
                posts.append(post)
            except:
                raise
                print 'Parsing Error!@B2'
        return posts

class SHC2(SourceHandlerC):
    '''
    淘财经
    '''
    status='error'
    def __init__(self,*args,**kwargs):
        self.ctime=str(int(time.time())-10)
        super(SHC2,self).__init__(*args,**kwargs)

    def update(self):
        text=self.browser.openlink('http://www.taoguba.com/recent_post.id?%s'%(self.ctime*1000))
        js=json.loads(text)
        self.ctime=str(int(time.time())-10)
        if js==10364: return 0
        pdb.set_trace()
        posts=[Post(d['content'],'',time=int(d['time']),source_id=self.source.id) for d in js['data']]
        pdb.set_trace()
        return res

    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        raise NotImplementedError()
 
    @inherit_docstring_from(SourceHandler)
    def get_list(self,pagecontent):
        tree=html.fromstring(pagecontent)
        lis=tree.xpath(u".//div[@class='answerBox']")
        posts=[]
        for li in lis:
            try:
                user=li.xpath(u".//a[@class='blue1']")[0].text
                content=li.xpath(u".//a[@class='cntcolor']")[0].text
                title=user+': '+content.strip('\r\n\t ')
                t=li.xpath(u".//a[@class='date']")[0].text.strip('\r\n\t ')
                t=time.mktime(datetime.strptime(t.encode('utf-8'),'%Y年%m月%d日 %H:%M').timetuple())

                post=Post(title,'',time=t,source_id=self.source.id)
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
    elif source.name=='互动易':
        return SHC0(source)
    elif source.name=='上证e互动':
        return SHC1(source)
    elif source.name=='淘财经':
        return SHC2(source)
    elif source.name=='未知源':
        return DummyHandler(source)
    else:
        raise ValueError

def get_groups(handlers):
    '''Get all groups.'''
    gs=[[],[],[]]
    for h in handlers:
        gs[h.group].append(h)
    return [GHandler(g) for g in gs]
