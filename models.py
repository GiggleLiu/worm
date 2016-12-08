#-*-coding:utf-8-*-

import requests,sqlite3,zlib,os,time,datetime,webbrowser
import pdb

__all__=['dbfile','Source','Post','save_post','get_sources','get_source',
        'get_posts_bysid','init_tables','init_sources','get_posts']

dbfile='data.db'

class Source(object):
    def __init__(self,name,baselink,id=-1):
        self.id=id
        if isinstance(baselink,unicode):
            baselink=baselink.encode('utf-8')
        if isinstance(name,unicode):
            name=name.encode('utf-8')
        self.baselink=baselink
        self.name=name

    def __str__(self):
        return '<s%s: %s> %s'%(self.id,self.name,self.baselink)

    def __repr__(self):
        return self.__str__()

    def get_page(self):
        '''Get the site page'''
        page=requests.get(self.baselink)
        if page.encoding=='ISO-8859-1': page.encoding='utf-8'
        res=page.content.decode(page.encoding)
        return res

class Post(object):
    '''Single post.'''
    def __init__(self,title,link,time,source_id,money=0,pagecontent='',id=-1):
        self.id=id
        if isinstance(title,unicode):
            title=title.encode('utf-8')
        if isinstance(link,unicode):
            link=link.encode('utf-8')
        if isinstance(pagecontent,buffer):
            pagecontent=zlib.decompress(pagecontent)
        self.title,self.link,self.time,self.source_id=title,link,time,source_id
        self.money,self.pagecontent=money,pagecontent

    def __str__(self):
        s='<标题: %s>\n时间: %s\n来源: %s%s\n链接: %s'%(self.title,datetime.datetime.utcfromtimestamp(self.time),self.source_id,('' if self.money==0 else '\n金额: %s万元'%self.money),self.link)
        return s

    def __repr__(self):
        return self.__str__()

    def __eq__(self,target):
        return self.title==target.title

    def formatted_str(self):
        '''Formatted string for display.'''
        info='{:<100} {:<20} {:<5}'.format(self.title,datetime.datetime.utcfromtimestamp(self.time),self.source_id.strip())
        link='{:<100}'.format(self.link)
        res='%s'%(info)
        return res

    def browse(self):
        '''View this post on browser.'''
        path=os.path.abspath('temp.html')
        url='file://'+path
        with open(path,'w') as f:
            f.write(self.pagecontent)
        f.close()
        webbrowser.open(url)

    def get_page(self):
        '''Get the detailed information page of post.'''
        page=requests.get(self.link)
        if page.encoding=='ISO-8859-1': page.encoding='utf-8'
        res=page.content.decode(page.encoding)
        return res

def save_post(post):
    '''Save a source or post.'''
    conn=sqlite3.connect(dbfile)
    try:
        conn.execute('''insert into post (title,time,link,source_id,money,pagecontent) values ('%s','%s','%s',%s,%s,?)'''\
                %(post.title,post.time,post.link,post.source_id,post.money),(sqlite3.Binary(zlib.compress(post.pagecontent)),))
        conn.commit()
        info=1
    except:
        info=0
    finally:
        conn.close()
        return info

def get_sources():
    '''Get all sources.'''
    conn=sqlite3.connect(dbfile)
    res=[Source(item[1],item[2],id=item[0]) for item in conn.execute('''select * from source''')]
    conn.close()
    return res

def get_posts():
    '''Get sources by source id.'''
    sqstr='''select * from post;'''
    conn=sqlite3.connect(dbfile)
    posts=[Post(title=item[1],time=item[2],link=item[3],id=item[0],source_id=item[4],money=item[5],pagecontent=item[6])\
            for item in conn.execute(sqstr)]
    conn.close()
    return posts

def get_source(sid):
    '''Get single source by id.'''
    conn=sqlite3.connect(dbfile)
    res=[Source(item[1],item[2],id=item[0]) for item in conn.execute('''select * from source where id=%s;'''%sid)]
    conn.close()
    return res

def get_posts_bysid(sid):
    '''Get sources by source id.'''
    sqstr='''select * from post where source_id='%s';'''%sid
    conn=sqlite3.connect(dbfile)
    posts=[Post(title=item[1],time=item[2],link=item[3],id=item[0],source_id=item[4],money=item[5],pagecontent=item[6])\
            for item in conn.execute(sqstr)]
    conn.close()
    return posts

def init_tables():
    '''initialize tables.'''
    if os.path.isfile(dbfile):
        print 'Skip creating database!'
        return
    conn=sqlite3.connect(dbfile)
    conn.execute('''create table source
            (id integer primary key autoincrement,
            name text unique not null,
            link text not null);''')
    conn.execute('''create table post
            (id integer primary key autoincrement,
            title text unique not null,
            time float not null,
            link text not null,
            source_id integer,
            money real,
            pagecontent binary,
            foreign key(source_id) references source(id));''')
    conn.commit()
    conn.close()

def init_sources():
    '''initialize sources.'''
    source_list=[
            (u'中国政府采购网','http://www.ccgp.gov.cn/ppp/pppzhbgg/'),
            (u'北京财政','http://www.bjcz.gov.cn/zfcg/cggg/sycjjggg/index.htm'),
            (u'广州市政府采购网','http://www.gzg2b.gov.cn/Sites/_Layouts/ApplicationPages/News/News.aspx?ColumnName=%e6%8b%9b%e6%a0%87%e7%bb%93%e6%9e%9c%e5%85%ac%e5%91%8a'),
            (u'云财经','http://www.yuncaijing.com/insider/main.html'),
            (u'证快讯','http://news.cnstock.com/bwsd/index.html'),
            (u'财联社','http://www.cailianpress.com'),
            (u'互动易','http://irm.cninfo.com.cn/ircs/sse/sseSubIndex.do?condition.type=7'),
            (u'上证e互动','http://sns.sseinfo.com/'),
            (u'淘财经','http://www.taoguba.com/')
            ]
    conn=sqlite3.connect(dbfile)
    for source in source_list:
        try:
            conn.execute('''insert into source (name,link) values ('%s','%s')'''%(source[0],source[1]))
        except:
            print 'Create Source Fail: %s.'%(source,)
    conn.commit()
    conn.close()
